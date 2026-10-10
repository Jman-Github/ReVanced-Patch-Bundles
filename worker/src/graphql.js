/* Independent implementation of the upstream read-only Hasura public role.
 * Reference: https://github.com/brosssh/revanced-external-bundles/blob/3a59398d667c83cd7033f859f3cb59237da92b3f/src/main/resources/hasura/metadata.json
 * No upstream backend source is incorporated. See docs/source-attribution.md.
 */
import {
  buildSchema, execute, getNamedType, getOperationAST, getVariableValues,
  isListType, isNonNullType, parse, validate, valueFromASTUntyped
} from "graphql";
import site from "../../config/site.json" with {type:"json"};
import { AsyncLocalStorage } from "node:async_hooks";
import { createPostgresMatcher } from "./postgres-regex.js";
import { mergeJobs } from "./jobs.js";
import { createPostgresComparator } from "../../shared/postgres-collation.js";
import { streamArguments, streamBatch } from "./streaming.js";
import { CatalogError, compareValues, configureAggregateMatcher, configureCaseFolder, configureRegexMatcher, configureTextComparator, filterResult, matches, pagination, selectRows } from "../../shared/catalog.js";

const regexContext = new AsyncLocalStorage();
const defaultComparator = createPostgresComparator(site.postgres_locale ?? "en_US.utf8");
configureTextComparator((left,right) => (regexContext.getStore()?.compare ?? defaultComparator)(left,right));
configureRegexMatcher((value, pattern, operator) =>
  (regexContext.getStore() ?? createPostgresMatcher())(value, pattern, operator));
configureCaseFolder(value => (regexContext.getStore() ?? createPostgresMatcher()).fold(value));

const definitions = {
  source: { id: "Int", catalog_id: "String", url: "String", enabled: "Boolean",
    unavailable_reason: "String", host: "String", namespace: "String", repo: "String" },
  source_metadata: { id: "Int", source_fk: "Int", owner_name: "String", repo_name: "String",
    owner_avatar_url: "String", repo_description: "String", repo_stars: "Int",
    repo_pushed_at: "String", is_repo_archived: "Boolean" },
  bundle: { id: "Int", catalog_id: "String", source_fk: "Int", source_id: "String",
    bundle_type: "String", ecosystem: "String", version: "String", created_at: "String",
    description: "String", download_url: "String", signature_download_url: "String",
    file_hash: "String", is_prerelease: "Boolean", is_latest: "Boolean",
    need_patches_update: "Boolean", patcher_failure_fingerprint: "String",
    metadata_status: "String", patcher_runtime: "String", extraction_status: "String",
    patch_count: "Int", release_status: "String" },
  patch: { id: "Int", catalog_id: "String", bundle_fk: "Int", bundle_id: "String",
    source_id: "String", name: "String", description: "String", use: "Boolean",
    metadata_status: "String", patch_metadata_version: "String" },
  package: { id: "Int", name: "String", version: "String" },
  patch_package: { package_fk: "Int", patch_fk: "Int", patch_id: "String" },
  refresh_jobs: { id: "Int", job_id: "String", job_type: "String", status: "String",
    error: "String", completed_at: "timestamptz", started_at: "timestamptz" }
};
// Omitted optional JSON fields have SQL NULL semantics in the public schema.
const scalarDefaults = Object.fromEntries(Object.entries(definitions).map(([kind, fields]) =>
  [kind, Object.fromEntries(Object.keys(fields).map(field => [field, null]))]));
function graphRow(kind, row) { return { ...scalarDefaults[kind], ...row, __kind: kind }; }

const objects = {
  source: { source_metadatum: "source_metadata" }, source_metadata: { source: "source" },
  bundle: { source: "source" }, patch: { bundle: "bundle" },
  patch_package: { package: "package", patch: "patch" }
};
const arrays = {
  source: { bundles: "bundle" }, bundle: { patches: "patch" },
  patch: { patch_packages: "patch_package" }, package: { patch_packages: "patch_package" }
};
const numericOperations = ["avg", "sum", "stddev", "stddev_pop", "stddev_samp",
  "variance", "var_pop", "var_samp"];
const scalarComparisons = ["String", "Int", "Float", "Boolean", "timestamptz"].map(type => {
  const text = type === "String" ? `
    _like: String, _ilike: String, _nlike: String, _nilike: String,
    _regex: String, _iregex: String, _nregex: String, _niregex: String,
    _similar: String, _nsimilar: String` : "";
  return `input ${type}_comparison_exp {
    _eq: ${type}, _neq: ${type}, _in: [${type}!], _nin: [${type}!],
    _is_null: Boolean, _gt: ${type}, _gte: ${type}, _lt: ${type}, _lte: ${type} ${text}
  }`;
}).join("\n");
const argsFor = name => `where: ${name}_bool_exp, order_by: [${name}_order_by!],
  limit: Int, offset: Int, distinct_on: [${name}_select_column!]`;
function schemaFor(name, fields) {
  const scalars = Object.entries(fields);
  const orderable = scalars.filter(([, type]) => type !== "Boolean");
  const numeric = scalars.filter(([, type]) => type === "Int");
  const booleans = scalars.filter(([, type]) => type === "Boolean");
  const objectFields = Object.entries(objects[name] ?? {});
  const arrayFields = Object.entries(arrays[name] ?? {});
  const extras = name === "bundle" ? "channels: [String!]!, import_urls: jsonb, release_url: String" :
    name === "patch" ? "options: jsonb, dependencies: [String!], compatiblePackages: jsonb" :
    name === "package" ? "versions: [String!]" : "";
  const aggregateDefs = ["min", "max", ...numericOperations].map(op => {
    const entries = op === "min" || op === "max" ? orderable : numeric;
    return entries.length ? `type ${name}_${op}_fields {
      ${entries.map(([key, type]) => key + ": " +
        (op === "sum" ? "bigint" : numericOperations.includes(op) ? "Float" : type)).join("\n")}
    }` : "";
  }).join("\n");
  const aggregateFields = ["min", "max", ...numericOperations].filter(op =>
    (op === "min" || op === "max" ? orderable : numeric).length)
    .map(op => `${op}: ${name}_${op}_fields`).join("\n");
  return `
    type ${name} {
      ${scalars.map(([key, type]) => key + ": " + type).join("\n")}
      ${objectFields.map(([key, type]) => key + ": " + type).join("\n")}
      ${arrayFields.map(([key, type]) => `${key}(${argsFor(type)}): [${type}!]!
        ${key}_aggregate(${argsFor(type)}): ${type}_aggregate!`).join("\n")}
      ${extras}
    }
    input ${name}_bool_exp {
      _and: [${name}_bool_exp!], _or: [${name}_bool_exp!], _not: ${name}_bool_exp
      ${scalars.map(([key, type]) => key + ": " + type + "_comparison_exp").join("\n")}
      ${[...objectFields, ...arrayFields].map(([key, type]) => key + ": " + type + "_bool_exp").join("\n")}
      ${arrayFields.map(([key, type]) => key + "_aggregate: " + type + "_aggregate_bool_exp").join("\n")}
    }
    input ${name}_order_by {
      ${scalars.map(([key]) => key + ": order_by").join("\n")}
      ${objectFields.map(([key, type]) => key + ": " + type + "_order_by").join("\n")}
      ${arrayFields.map(([key, type]) => key + "_aggregate: " + type + "_aggregate_order_by").join("\n")}
    }
    enum ${name}_select_column { ${scalars.map(([key]) => key).join(" ")} }
    ${aggregateDefs}
    input ${name}_aggregate_bool_exp {
      count: ${name}_aggregate_bool_exp_count
      ${booleans.length ? ["bool_and", "bool_or"].map(op =>
        op + ": " + name + "_aggregate_bool_exp_" + op).join("\n") : ""}
      ${numeric.length ? ["min", "max", ...numericOperations].map(op =>
        op + ": " + name + "_aggregate_bool_exp_" + op).join("\n") : ""}
    }
    ${booleans.length ? ["bool_and", "bool_or"].map(op => `
      enum ${name}_select_column_${name}_aggregate_bool_exp_${op}_arguments_columns {
        ${booleans.map(([key]) => key).join(" ")}
      }
      input ${name}_aggregate_bool_exp_${op} {
        arguments: ${name}_select_column_${name}_aggregate_bool_exp_${op}_arguments_columns!,
        distinct: Boolean, filter: ${name}_bool_exp, predicate: Boolean_comparison_exp!
      }`).join("\n") : ""}
    input ${name}_aggregate_bool_exp_count {
      arguments: [${name}_select_column!], distinct: Boolean,
      filter: ${name}_bool_exp, predicate: Int_comparison_exp!
    }
    ${numeric.length ? `enum ${name}_numeric_column { ${numeric.map(([key]) => key).join(" ")} }` : ""}
    ${numeric.length ? ["min", "max", ...numericOperations].map(op =>
      `input ${name}_aggregate_bool_exp_${op} {
        arguments: ${name}_numeric_column!, distinct: Boolean,
        filter: ${name}_bool_exp, predicate: Float_comparison_exp!
      }`).join("\n") : ""}
    type ${name}_aggregate_fields {
      count(columns: [${name}_select_column!], distinct: Boolean): Int!
      ${aggregateFields}
    }
    type ${name}_aggregate { aggregate: ${name}_aggregate_fields, nodes: [${name}!]! }
    input ${name}_aggregate_order_by {
      count: order_by
      ${["min", "max", ...numericOperations].filter(op =>
        (op === "min" || op === "max" ? orderable : numeric).length)
        .map(op => op + ": " + name + "_" + op + "_order_by").join("\n")}
    }
    ${["min", "max", ...numericOperations].map(op => {
      const entries = op === "min" || op === "max" ? orderable : numeric;
      return entries.length ? `input ${name}_${op}_order_by {
        ${entries.map(([key]) => key + ": order_by").join("\n")}
      }` : "";
    }).join("\n")}
  `;
}
const roots = Object.keys(definitions).flatMap(name => [
  `${name}(${argsFor(name)}${name === "patch" ? ", q: String, package_name: String, bundle_id: String" : ""}): [${name}!]!`,
  name === "patch_package" ? `${name}_by_pk(package_fk: Int!, patch_fk: Int!): ${name}` :
    `${name}_by_pk(id: Int!): ${name}`,
  name === "refresh_jobs" ? "" : `${name}_aggregate(${argsFor(name)}
    ${name === "patch" ? ", package_name: String, bundle_id: String" : ""}): ${name}_aggregate!`
]).join("\n");
const streams = Object.keys(definitions).map(name =>
  `${name}_stream(batch_size: Int!, cursor: [${name}_stream_cursor_input]!,
    where: ${name}_bool_exp): [${name}!]!`).join("\n");
const streamInputs = Object.entries(definitions).map(([name, fields]) => `
  input ${name}_stream_cursor_input {
    initial_value: ${name}_stream_cursor_value_input!, ordering: cursor_ordering
  }
  input ${name}_stream_cursor_value_input {
    ${Object.entries(fields).map(([key,type]) => key + ": " + type).join("\n")}
  }`).join("\n");
export const schema = buildSchema(`
  scalar jsonb
  scalar bigint
  scalar timestamptz
  enum cursor_ordering { ASC DESC }
  ${streamInputs}
  enum order_by { asc desc asc_nulls_first asc_nulls_last desc_nulls_first desc_nulls_last }
  ${scalarComparisons}
  ${Object.entries(definitions).map(([name, fields]) => schemaFor(name, fields)).join("\n")}
  type query_root { ${roots} release(${argsFor("bundle")}): [bundle!]! }
  type subscription_root { ${roots} ${streams} release(${argsFor("bundle")}): [bundle!]! }
  schema { query: query_root, subscription: subscription_root }
`);
for (const name of ["jsonb", "timestamptz", "bigint"]) {
  const scalar = schema.getType(name);
  scalar.serialize = value => value;
  scalar.parseValue = value => value;
  scalar.parseLiteral = node => valueFromASTUntyped(node);
}

function containsKey(value, key) {
  return Boolean(value && typeof value === "object" &&
    (Object.hasOwn(value, key) || Object.values(value).some(v => containsKey(v, key))));
}
function equality(where, path) {
  let value = where;
  for (const key of path) value = value?.[key];
  return value?._eq ?? undefined;
}
function indexedPackage(where) {
  const names = new Set();
  function visit(value) {
    if (!value || typeof value !== "object") return;
    const name = equality(value, ["patch_packages", "package", "name"]);
    if (name) names.add(name);
    // Only conjunctions constrain the returned patch itself. A predicate on
    // another patch through its bundle must not narrow this patch's packages.
    (value._and ?? []).forEach(visit);
  }
  visit(where);
  return names.size === 1 ? [...names][0] : undefined;
}
function aggregate(rows, args = {}) {
  const selected = args.limit === 0 ? { data: [] } : selectRows(rows,
    { ...args, limit: args.limit ?? Math.max(1, rows.length) }, Math.max(100, rows.length));
  const data = selected.data;
  // Aggregate values share the node selection (including distinct, offset and limit).
  const values = {};
  values.count = ({ columns, distinct } = {}) => {
    const counted = columns?.length ? data.filter(row => columns.every(c => row[c] != null)) : data;
    return distinct && columns?.length ? new Set(counted.map(row =>
      JSON.stringify(columns.map(c => row[c])))).size : counted.length;
  };
  for (const op of ["min", "max", ...numericOperations]) {
    values[op] = { __aggregateKind: rows[0]?.__kind };
    const keys = Object.keys(definitions[rows[0]?.__kind] ?? {});
    for (const key of keys) {
      const numbers = data.map(row => row[key]).filter(v => v != null);
      if (!numbers.length) { values[op][key] = null; continue; }
      if (op === "min" || op === "max") {
        values[op][key] = numbers.reduce((a,b) => {
          const timestamp = definitions[rows[0]?.__kind]?.[key] === "timestamptz";
          const compared = compareValues(a,b,timestamp);
          return op === "min" ? (compared < 0 ? a : b) : (compared > 0 ? a : b);
        });
      } else if (numbers.every(v => typeof v === "number")) {
        const sum = numbers.reduce((a,b) => a+b, 0), mean = sum / numbers.length;
        const squares = numbers.reduce((a,b) => a + (b-mean)**2, 0);
        const sample = ["stddev", "stddev_samp", "variance", "var_samp"].includes(op);
        const variance = sample && numbers.length < 2 ? null : squares / (numbers.length - Number(sample));
        values[op][key] = op === "sum" ? sum : op === "avg" ? mean : variance == null ? null :
          op.startsWith("stddev") ? Math.sqrt(variance) : variance;
      }
    }
  }
  return { aggregate: values, nodes: () => args.limit === 0 ? [] : selectRows(rows, args).data };
}
configureAggregateMatcher((rows, condition) => {
  const results = Object.entries(condition).map(([op, args]) => {
    if (args == null) return true;
    let selected = rows.filter(row => matches(row, args.filter ?? {}));
    if (op === "count") {
      const value = aggregate(selected).aggregate.count({
        columns: args.arguments, distinct: args.distinct
      });
      return filterResult({ value }, { value: args.predicate });
    }
    if (args.distinct) {
      const seen = new Set();
      selected = selected.filter(row => {
        const value = row[args.arguments];
        if (seen.has(value)) return false;
        seen.add(value); return true;
      });
    }
    let value;
    if (op === "bool_and" || op === "bool_or") {
      // PostgreSQL ignores NULL inputs and yields NULL for an empty/all-NULL set.
      const values = selected.map(row => row[args.arguments]).filter(v => v != null);
      value = values.length ? (op === "bool_and" ? values.every(Boolean) : values.some(Boolean)) : null;
    } else value = aggregate(selected).aggregate[op]?.[args.arguments] ?? null;
    return filterResult({ value }, { value: args.predicate });
  });
  return results.includes(false) ? false : results.includes(null) ? null : true;
});
function enforceComplexity(document, operation, variables, rootSizes = {}) {
  const fragments = new Map(document.definitions.filter(d => d.kind === "FragmentDefinition")
    .map(d => [d.name.value, d]));
  let fields = 0, cost = 0;
  function walk(set, depth, multiplier, parentType, stack = new Set()) {
    if (!set) return;
    const introspectionType = parentType?.name?.startsWith("__");
    if (depth > (introspectionType ? 24 : 8))
      throw new CatalogError("GraphQL depth exceeds 8");
    for (const node of set.selections) {
      if (++fields > 300) throw new CatalogError("GraphQL field count exceeds 300");
      if (node.kind === "FragmentSpread") {
        if (stack.has(node.name.value)) throw new CatalogError("Cyclic GraphQL fragment");
        walk(fragments.get(node.name.value)?.selectionSet, depth, multiplier, parentType,
             new Set([...stack, node.name.value]));
      } else if (node.kind === "InlineFragment") {
        walk(node.selectionSet, depth, multiplier, parentType, stack);
      } else {
        const arg = node.arguments?.find(a => ["limit", "batch_size"].includes(a.name.value));
        const responseKey = node.alias?.value ?? node.name.value;
        const supplied = depth === 1 && Object.hasOwn(rootSizes, responseKey) ?
          rootSizes[responseKey] : arg ? valueFromASTUntyped(arg.value, variables) : 25;
        const fieldType = parentType?.getFields?.()[node.name.value]?.type ??
          (node.name.value === "__schema" ? schema.getType("__Schema") :
           node.name.value === "__type" ? schema.getType("__Type") : undefined);
        const nullable = isNonNullType(fieldType) ? fieldType.ofType : fieldType;
        const factor = introspectionType || node.name.value.startsWith("__") ? 1 :
          isListType(nullable) ? Math.max(1, Number(supplied ?? 25)) : 1;
        if (!Number.isInteger(factor) || factor < 0 || factor > 100)
          throw new CatalogError("GraphQL list limit must be 1–100");
        cost += multiplier;
        if (cost > 20000) throw new CatalogError("GraphQL query complexity exceeds 20000");
        walk(node.selectionSet, depth + 1, multiplier * factor,
             fieldType ? getNamedType(fieldType) : undefined, stack);
      }
    }
  }
  walk(operation.selectionSet, 1, 1,
    operation.operation === "subscription" ? schema.getSubscriptionType() : schema.getQueryType());
}

export function withPostgresLocale(locale, callback) {
  const matcher = createPostgresMatcher(locale);
  matcher.compare = createPostgresComparator(locale);
  return regexContext.run(matcher, callback);
}
export function runGraphQL(catalog, payload, options = {}) {
  return withPostgresLocale(catalog.regexLocale ?? site.postgres_locale ?? "en_US.utf8",
    () => executeQuery(catalog, payload, options));
}
export function subscriptionPayload(payload) {
  if (!payload || typeof payload.query !== "string" || payload.query.length > 20000)
    throw new CatalogError("Expected a GraphQL operation of at most 20000 characters");
  const document = parse(payload.query, { maxTokens: 4000 });
  const operation = getOperationAST(document, payload.operationName);
  if (!operation || !["query", "subscription"].includes(operation.operation))
    throw new CatalogError("Only read-only queries and subscriptions are supported");
  const errors = validate(schema, document);
  if (errors.length) throw new CatalogError(errors.map(error => error.message).join("; "));
  const stream = operation.operation === "subscription";
  return { payload, stream };
}
async function executeQuery(catalog, payload, options) {
  if (!payload || typeof payload !== "object" || Array.isArray(payload) ||
      (payload.variables != null && (typeof payload.variables !== "object" || Array.isArray(payload.variables))) ||
      (payload.operationName != null && typeof payload.operationName !== "string"))
    throw new CatalogError("Expected one GraphQL query object with optional variables and operationName");
  if (typeof payload.query !== "string" || payload.query.length > 20000)
    throw new CatalogError("GraphQL query must contain at most 20000 characters");
  let document;
  try { document = parse(payload.query, { maxTokens: 4000 }); }
  catch (error) { throw new CatalogError(error.message); }
  const operation = getOperationAST(document, payload.operationName);
  if (!operation || (operation.operation !== "query" &&
      !(operation.operation === "subscription" && options.subscription)))
    throw new CatalogError("Only named or unambiguous read-only queries are supported");
  const errors = validate(schema, document);
  if (errors.length) return { errors: errors.map(e => ({ message: e.message })) };
  const variables = getVariableValues(schema, operation.variableDefinitions ?? [], payload.variables ?? {});
  if (variables.errors) return { errors: variables.errors.map(e => ({ message: e.message })) };
  enforceComplexity(document, operation, variables.coerced);
  const sourceRows = await catalog.sources(), bundleRows = await catalog.bundles();
  const sourceMap = new Map(), bundleMap = new Map();
  const tables = { source: [], bundle: [], source_metadata: [] };
  sourceRows.forEach((row, i) => {
    const source = { ...graphRow("source", row), id: row.legacy_id ?? i + 1,
      catalog_id: row.id, unavailable_reason: row.unavailable_reason ?? null, bundles: [] };
    const metadata = { ...graphRow("source_metadata", row.source_metadatum),
      id: row.source_metadatum.id ?? i + 1, source_fk: source.id, source };
    source.source_metadatum = metadata;
    sourceMap.set(row.id, source);
    tables.source.push(source); tables.source_metadata.push(metadata);
  });
  bundleRows.forEach((row, i) => {
    const source = sourceMap.get(row.source_id);
    const bundle = { ...graphRow("bundle", row), id: row.legacy_id ?? i + 1,
      catalog_id: row.id, source_fk: source.id, source, patches: [],
      patcher_failure_fingerprint: row.patcher_failure_fingerprint ?? null };
    bundleMap.set(row.id, bundle); source.bundles.push(bundle); tables.bundle.push(bundle);
  });
  let packagePromise;
  async function packages() {
    packagePromise ??= (async () => {
      const rows = catalog.manifest.files["package-records.json"] ?
        await catalog.file("package-records.json") :
        (await catalog.file("packages.json")).flatMap(p =>
          (p.versions.length ? p.versions : [null]).map(version => ({ ...p, version })));
      tables.package = rows.map((row, i) => ({ ...graphRow("package", row),
        id: row.id ?? i + 1, patch_packages: [] }));
      return new Map(tables.package.map(row => [JSON.stringify([row.name, row.version]), row]));
    })();
    return packagePromise;
  }
  const patchesByHash = new Map();
  async function joinPatches(rows) {
    const packageMap = await packages();
    for (const row of rows) {
      if (patchesByHash.has(row.id)) continue;
      const bundle = bundleMap.get(row.bundle_id);
      const patch = { ...graphRow("patch", row), id: row.legacy_id ?? patchesByHash.size + 1,
        catalog_id: row.id, bundle_fk: bundle.id, bundle, patch_packages: [] };
      for (const pkg of row.packages) for (const version of pkg.versions.length ? pkg.versions : [null]) {
        const packageRow = packageMap.get(JSON.stringify([pkg.name, version]));
        if (!packageRow) throw new CatalogError("Package relationship index unavailable", 503);
        const link = { __kind: "patch_package", package_fk: packageRow.id, patch_fk: patch.id,
          patch_id: row.id, package: packageRow, patch };
        patch.patch_packages.push(link); packageRow.patch_packages.push(link);
      }
      patchesByHash.set(row.id, patch); bundle.patches.push(patch);
    }
    for (const source of tables.source)
      source.bundles_aggregate = aggregateOrder(source.bundles);
    for (const bundle of tables.bundle)
      bundle.patches_aggregate = aggregateOrder(bundle.patches);
    for (const patch of patchesByHash.values())
      patch.patch_packages_aggregate = aggregateOrder(patch.patch_packages);
    for (const pkg of tables.package)
      pkg.patch_packages_aggregate = aggregateOrder(pkg.patch_packages);
    return rows.map(row => patchesByHash.get(row.id));
  }
  function aggregateOrder(rows) {
    const value = aggregate(rows, { limit: rows.length || 1 }).aggregate;
    return { ...value, count: rows.length };
  }
  function positive(where, path) {
    // Direct predicates and conjunctions remain mandatory alongside OR/NOT predicates.
    // Never descend into an OR/NOT branch when deriving an index constraint.
    const direct = equality(where, path);
    if (direct != null) return direct;
    for (const nested of where?._and ?? []) {
      const value = positive(nested, path);
      if (value != null) return value;
    }
  }
  async function loadPatches(args, scopedBundle, scopedPackage, parentKind) {
    const where = args.where ?? {};
    const numericBundle = (parentKind === "bundle" ? positive(where, ["id"]) : undefined) ??
      positive(where, ["bundle_fk"]) ?? positive(where, ["bundle", "id"]);
    const canonicalBundle = args.bundle_id ?? positive(where, ["bundle_id"]) ??
      positive(where, ["bundle", "catalog_id"]);
    const sourceUrl = (parentKind === "source" ? positive(where, ["url"]) : undefined) ??
      positive(where, ["bundle", "source", "url"]) ?? positive(where, ["source", "url"]);
    const metadataId = parentKind === "source_metadata" ? positive(where, ["id"]) : undefined;
    const sourceId = (parentKind === "source" ? positive(where, ["id"]) : undefined) ??
      (metadataId != null ? tables.source_metadata.find(row => row.id === metadataId)?.source_fk : undefined) ??
      positive(where, ["bundle", "source_fk"]) ?? positive(where, ["source_fk"]);
    const ids = scopedBundle ? [scopedBundle.catalog_id] :
      canonicalBundle ? [canonicalBundle] :
      numericBundle != null || sourceUrl || sourceId != null ?
      tables.bundle.filter(b => (numericBundle == null || b.id === numericBundle) &&
        (!sourceUrl || b.source.url === sourceUrl) && (sourceId == null || b.source_fk === sourceId))
        .map(b => b.catalog_id) : undefined;
    const rows = (await catalog.patchRows({ all: true,
      bundle_ids: ids, package: scopedPackage ?? args.package_name ?? indexedPackage(where),
      patch_id: parentKind ? undefined : positive(where, ["id"]), patch_ids: args.patch_ids, q: args.q,
      include_unverified: true })).rows;
    await joinPatches(rows);
    if (containsKey(where, "patches") || containsKey(where, "patches_aggregate") ||
        containsKey(args.order_by, "patches_aggregate")) {
      // A predicate on another patch needs complete sibling rows. Scope that
      // hydration to the selected bundles, or their sources when source.bundles
      // is traversed, without narrowing the patch rows returned by this query.
      let relatedIds = ids ?? [...new Set(rows.map(row => row.bundle_id))];
      if (containsKey(where, "bundles") || containsKey(args.order_by, "bundles_aggregate")) {
        const owners = new Set(relatedIds.map(id => bundleMap.get(id)?.source_fk));
        relatedIds = tables.bundle.filter(bundle => owners.has(bundle.source_fk))
          .map(bundle => bundle.catalog_id);
      }
      await joinPatches((await catalog.patchRows({all:true, bundle_ids:relatedIds,
        include_unverified:true})).rows);
    }
    return rows.map(row => patchesByHash.get(row.id));
  }
  const relationLoads = new Map();
  function narrowed(rows, condition) {
    // Mandatory equalities keep source/package filters within their shard scope.
    // Nullable comparisons cannot prune rows: SQL UNKNOWN may still combine
    // with a false relationship predicate under NOT.
    for (const key of Object.keys(definitions[rows[0]?.__kind] ?? {})) {
      const expected = positive(condition, [key]);
      if (expected != null && rows.every(row => row[key] != null))
        rows = rows.filter(row => matches(row, {[key]:{_eq:expected}}));
    }
    return rows;
  }
  async function hydrateRelations(rows, condition) {
    if (!rows.length || !condition || typeof condition !== "object") return;
    if (Array.isArray(condition)) {
      for (const part of condition) await hydrateRelations(rows, part);
      return;
    }
    rows = narrowed(rows, condition);
    if (!rows.length) return;
    const kind = rows[0].__kind;
    for (const [key, value] of Object.entries(condition)) {
      if (key === "_and" || key === "_or") {
        for (const part of value ?? []) await hydrateRelations(rows, part);
        continue;
      }
      if (key === "_not") { await hydrateRelations(rows, value); continue; }
      const isAggregate = key.endsWith("_aggregate");
      const relation = isAggregate ? key.slice(0, -10) : key;
      if (!arrays[kind]?.[relation] && !objects[kind]?.[relation]) continue;
      // Reverse relationships must include peers outside the outer query's
      // patch/bundle scope. Load only the referenced bundle or package shards.
      if (kind === "bundle" && relation === "patches") {
        const ids = [...new Set(rows.map(row => row.catalog_id))];
        const missing = ids.filter(id => !relationLoads.has("bundle:" + id));
        if (missing.length) {
          const pending = catalog.patchRows({all:true,bundle_ids:missing,include_unverified:true})
            .then(result => joinPatches(result.rows));
          for (const id of missing) relationLoads.set("bundle:" + id, pending);
        }
        await Promise.all(ids.map(id => relationLoads.get("bundle:" + id)));
      } else if (kind === "package" && relation === "patch_packages") {
        const names = [...new Set(rows.map(row => row.name))];
        for (const name of names) if (!relationLoads.has("package:" + name))
          relationLoads.set("package:" + name,
            catalog.patchRows({all:true,package:name,include_unverified:true})
              .then(result => joinPatches(result.rows)));
        await Promise.all(names.map(name => relationLoads.get("package:" + name)));
      }
      const related = [...new Set(rows.flatMap(row => row[relation] ?? []))];
      if (isAggregate) {
        for (const args of Object.values(value ?? {}))
          await hydrateRelations(related, args?.filter);
      } else await hydrateRelations(related, value);
    }
  }
  async function prepared(rows, args) {
    rows = narrowed(rows, args.where);
    await hydrateRelations(rows, args.where);
    await hydrateRelations(rows, args.order_by);
    return rows;
  }
  async function selected(rows, args) {
    return args.limit === 0 ? [] : selectRows(await prepared(rows, args), args).data;
  }
  async function rowsFor(kind, args) {
    const where = args.where ?? {};
    if (kind === "patch") return loadPatches(args);
    if (kind === "patch_package") {
      const packageId = positive(where, ["package_fk"]) ?? positive(where, ["package", "id"]);
      if (packageId != null) await packages();
      const packageRow = packageId != null ? tables.package.find(row => row.id === packageId) : undefined;
      if (packageId != null && !packageRow) return [];
      const pkg = positive(where, ["package", "name"]) ?? packageRow?.name;
      const patchId = positive(where, ["patch_fk"]);
      const patches = await loadPatches({ ...args,
        where: patchId != null ? {_and:[where, {id:{_eq:patchId}}]} : where }, undefined, pkg);
      return patches.flatMap(patch => patch.patch_packages);
    }
    if (kind === "package") {
      await packages();
      const id = positive(where, ["id"]);
      if (id != null && !tables.package.some(row => row.id === id)) return [];
      if (containsKey(where, "patch_packages") || containsKey(where, "patch_packages_aggregate") ||
          containsKey(args.order_by, "patch_packages_aggregate")) {
        const name = positive(where, ["name"]) ??
          tables.package.find(p => p.id === positive(where, ["id"]))?.name;
        await loadPatches(args, undefined, name, "package");
      }
      return tables.package;
    }
    if (kind === "refresh_jobs") {
      if (!tables.refresh_jobs) {
        const recorded = catalog.manifest.files["refresh-jobs.json"] ?
          await catalog.file("refresh-jobs.json") : [];
        let live = [];
        try { live = catalog.liveJobs ? await catalog.liveJobs() : []; }
        catch (error) { if (!recorded.length) throw error; }
        tables.refresh_jobs = mergeJobs(recorded, live).map(row => graphRow(kind, row));
      }
      return tables.refresh_jobs;
    }
    if (kind === "source_metadata") {
      const id = positive(where, ["id"]);
      if (id != null && !tables.source_metadata.some(row => row.id === id)) return [];
    }
    if (containsKey(where, "patches") || containsKey(where, "patches_aggregate") ||
        containsKey(args.order_by, "patches_aggregate")) {
      await loadPatches(args, undefined, undefined, kind);
    }
    for (const source of tables.source) source.bundles_aggregate = aggregateOrder(source.bundles);
    return tables[kind];
  }
  const rootValues = {};
  const streamState = { cursor: { ...(options.cursor ?? {}) }, empty: true };
  let cursorStream = false;
  for (const kind of Object.keys(definitions)) {
    rootValues[kind] = async args => selected(await rowsFor(kind, args), args);
    rootValues[kind + "_aggregate"] = async args =>
      aggregate(await prepared(await rowsFor(kind, args), args), args);
    rootValues[kind + "_by_pk"] = async args => {
      const where = kind === "patch_package" ?
        { package_fk: { _eq: args.package_fk }, patch_fk: { _eq: args.patch_fk } } :
        { id: { _eq: args.id } };
      return (await rowsFor(kind, { where })).find(row => matches(row, where)) ?? null;
    };
  }
  const defaultPatchRoot = rootValues.patch;
  rootValues.patch = async args => {
    const order = args.order_by ?? [{id:"asc"}];
    const simpleOrder = order.length === 1 && Object.keys(order[0]).length === 1 &&
      ["asc","desc"].includes(order[0].id);
    const idOnly = !args.where || !Object.keys(args.where).length ||
      (Object.keys(args.where).length === 1 && Object.hasOwn(args.where,"id"));
    if (idOnly && !args.q && !args.package_name &&
        !args.bundle_id && !args.distinct_on?.length && simpleOrder) {
      const index = await catalog.file("patch-index.json");
      if (index.patch_ids) {
        if (args.limit === 0) return [];
        const {limit,offset} = pagination(args);
        const ids = Object.keys(index.patch_ids).map(Number)
          .filter(id => matches({id},args.where ?? {})).sort((a,b)=>a-b);
        if (order[0].id === "desc") ids.reverse();
        const rows = await loadPatches({patch_ids:ids.slice(offset,offset+limit)});
        return selected(rows,{...args,offset:0});
      }
    }
    return defaultPatchRoot(args);
  };
  const defaultPatchAggregate = rootValues.patch_aggregate;
  rootValues.patch_aggregate = async args => {
    if (!Object.keys(args).length && catalog.manifest.files["patch-statistics.json"]) {
      const stats = await catalog.file("patch-statistics.json");
      const locale = String(catalog.regexLocale ?? site.postgres_locale ?? "en_US.utf8")
        .toLowerCase().replace(/[-_.]/g,"");
      const profile = ["c","posix","cutf8"].includes(locale) ? "C" : "en_US.utf8";
      const extrema = stats.text_extrema?.[profile];
      const aggregates = {...stats.aggregate};
      for (const op of ["min","max"]) aggregates[op] = extrema ?
        {...aggregates[op],...extrema[op]} :
        async () => (await defaultPatchAggregate({})).aggregate[op];
      return { aggregate: {...aggregates,count:({columns,distinct}={})=>{
        if (!columns?.length) return stats.count;
        if (columns.length > 1) {
          if (distinct) throw new CatalogError("Narrow the patch filter for multi-column distinct counts",422);
          const required = columns.reduce((mask,key)=>mask | (1 << stats.columns.indexOf(key)),0);
          return Object.entries(stats.null_masks).reduce((total,[mask,count]) =>
            total + ((Number(mask) & required) === 0 ? count : 0),0);
        }
        return (distinct ? stats.distinct : stats.nonnull)[columns[0]] ?? 0;
      }}, nodes:()=>rootValues.patch({}) };
    }
    return defaultPatchAggregate(args);
  };
  rootValues.release = rootValues.bundle;
  for (const kind of Object.keys(definitions)) {
    rootValues[kind + "_stream"] = async (args, info) => {
      cursorStream = true;
      const key = info.path.key;
      const selection = streamArguments(args, streamState.cursor[key]);
      let batch;
      // Unique numeric patch IDs can use the compact index, avoiding a broad
      // scan while keeping the same shard and response budgets.
      if (kind === "patch" && selection.columns.length === 1 &&
          selection.columns[0].name === "id") {
        const id = selection.where._and[1]._or[0];
        const where = !args.where || !Object.keys(args.where).length ? id : selection.where;
        const data = await rootValues.patch({...selection,where});
        batch = {data,cursor:data.length ? [data.at(-1).id] : null};
      } else {
        const rows = await prepared(await rowsFor(kind,selection),selection);
        batch = streamBatch(rows,selection);
      }
      // WITH TIES may return more rows than batch_size. Charge the full batch
      // before GraphQL expands its nested relationships.
      enforceComplexity(document, operation, variables.coerced, {[key]:batch.data.length});
      if (batch.cursor) { streamState.cursor[key] = batch.cursor; streamState.empty = false; }
      return batch.data;
    };
  }
  const result = await execute({
    schema, document, rootValue: rootValues, variableValues: variables.coerced,
    operationName: payload.operationName,
    fieldResolver: async (source, args, context, info) => {
      if (["query_root","subscription_root"].includes(info.parentType.name))
        return rootValues[info.fieldName]?.(args,info);
      const field = info.fieldName;
      if (source?.__kind === "bundle" && field === "description")
        return (await catalog.file("bundles/" + source.catalog_id + ".json")).description;
      const isAggregate = field.endsWith("_aggregate");
      const relation = isAggregate ? field.slice(0, -10) : field;
      if (arrays[source?.__kind]?.[relation]) {
        let rows;
        if (source.__kind === "bundle") rows = await loadPatches(args, source);
        else if (source.__kind === "package") {
          await loadPatches(args, undefined, source.name);
          rows = source.patch_packages;
        } else if (source.__kind === "source") {
          if (containsKey(args.where, "patches") || containsKey(args.where, "patches_aggregate") ||
              containsKey(args.order_by, "patches_aggregate"))
            await loadPatches({where:{_and:[args.where ?? {}, {source_fk:{_eq:source.id}}]}},
                              undefined, undefined, "bundle");
          rows = source.bundles;
        } else rows = source[relation];
        return isAggregate ? aggregate(await prepared(rows, args), args) : selected(rows, args);
      }
      const value = source?.[field];
      return typeof value === "function" ? value(args) : value;
    }
  });
  return cursorStream ? {...result, extensions:{registryStream:streamState}} : result;
}
