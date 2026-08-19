from scripts.generate_patch_list_catalog import format_compatible_packages


def test_compatible_packages_falls_back_to_target_versions() -> None:
    apps, versions = format_compatible_packages(
        [
            {
                "name": "RailOne",
                "targets": [
                    {"version": "2.1.62"},
                    {"version": None},
                    {"version": "2.1.62"},
                    {"version": "2.1.63"},
                ],
            }
        ]
    )

    assert apps == "RailOne"
    assert versions == "2.1.62, 2.1.63"


def test_compatible_packages_respects_explicit_null_versions() -> None:
    apps, versions = format_compatible_packages(
        [{"name": "RailOne", "versions": None, "targets": [{"version": "2.1.62"}]}]
    )

    assert apps == "RailOne"
    assert versions == "All versions"
