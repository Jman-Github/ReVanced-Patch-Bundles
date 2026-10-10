/* Hasura streaming cursors, independently implemented for immutable snapshots.
 * Reference: https://hasura.io/docs/2.0/subscriptions/postgres/streaming/index/
 */
import { CatalogError, compareValues, isTimestampField, selectRows } from "../../shared/catalog.js";

export function streamArguments(args, previous) {
  if (!Number.isInteger(args.batch_size) || args.batch_size < 1 || args.batch_size > 100)
    throw new CatalogError("GraphQL stream batch_size must be 1–100");
  const columns = [];
  for (const item of args.cursor ?? []) {
    if (!item) continue;
    for (const [name, value] of Object.entries(item.initial_value ?? {})) {
      if (value == null) continue;
      if (columns.some(column => column.name === name))
        throw new CatalogError("A stream cursor column may only be specified once");
      columns.push({ name, value, direction: item.ordering === "DESC" ? "desc" : "asc" });
    }
  }
  if (!columns.length) throw new CatalogError("A stream cursor requires a non-null initial value");
  if (previous) columns.forEach((column, index) => { column.value = previous[index]; });
  const after = columns.map((column, index) => Object.fromEntries([
    ...columns.slice(0, index).map(before => [before.name, { _eq: before.value }]),
    [column.name, { [column.direction === "asc" ? "_gt" : "_lt"]: column.value }]
  ]));
  return { columns, where: { _and: [args.where ?? {}, { _or: after }] },
    order_by: columns.map(column => ({ [column.name]: column.direction })),
    limit: args.batch_size };
}

export function streamBatch(rows, selection) {
  const ordered = rows.length ? selectRows(rows, {
    ...selection, limit: rows.length
  }, Math.max(100, rows.length)).data : [];
  const last = ordered[Math.min(selection.limit, ordered.length) - 1];
  let end = Math.min(selection.limit, ordered.length);
  // Hasura uses WITH TIES: don't skip rows sharing the last cursor value.
  const tied = row => selection.columns.every(column => compareValues(
    row[column.name], last[column.name], isTimestampField(row, column.name)) === 0);
  while (end < ordered.length && tied(ordered[end])) end++;
  if (end > 100) throw new CatalogError(
    "Stream cursor ties exceed 100 rows; use a unique cursor or narrow the filter", 422);
  const data = ordered.slice(0, end);
  return { data, cursor: data.length ?
    selection.columns.map(column => data.at(-1)[column.name]) : null };
}
