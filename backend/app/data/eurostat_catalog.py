"""Eurostat regional dataset catalog for Romania."""

EUROSTAT_CATALOG: list[dict] = [
    {
        "code": "eurostat.demo_r_d3dens.population_density",
        "dataset_code": "demo_r_d3dens",
        "label": "Densitate populație",
        "unit": "pers./km²",
        "theme": "demografie",
        "geo_level": "county",
        "nuts_level": 3,
        "filters": {},
    },
    {
        "code": "eurostat.demo_r_pjanaggr3.population",
        "dataset_code": "demo_r_pjanaggr3",
        "label": "Populație (1 ianuarie)",
        "unit": "persoane",
        "theme": "demografie",
        "geo_level": "county",
        "nuts_level": 3,
        "filters": {"sex": "T", "age": "TOTAL", "unit": "NR"},
    },
    {
        "code": "eurostat.nama_10r_3gdp.gdp_hab",
        "dataset_code": "nama_10r_3gdp",
        "label": "PIB pe locuitor",
        "unit": "EUR pe locuitor",
        "theme": "economie",
        "geo_level": "county",
        "nuts_level": 3,
        "filters": {"unit": "EUR_HAB"},
    },
    {
        "code": "eurostat.lfst_r_lfu3rt.unemployment",
        "dataset_code": "lfst_r_lfu3rt",
        "label": "Rată șomaj (regiune NUTS2)",
        "unit": "%",
        "theme": "munca",
        "geo_level": "region",
        "nuts_level": 2,
        "filters": {"sex": "T", "age": "Y15-74", "unit": "PC", "isced11": "TOTAL"},
    },
]
