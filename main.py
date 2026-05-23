from src.extract import Extract
from src.load import Load

ext = Extract()
ld = Load()

# br = ext.extract_country("Brazil")
# ld.create_sqlite_table(br, "universidades", "uni_br")
# ld.insert_in_mongo(br, "universidades", "uni_br")

# it = ext.extract_country("Italy")
# ld.create_sqlite_table(it, "universidades", "uni_it")
# ld.insert_in_mongo(it, "universidades", "uni_it")

meios_pag = ext.extract_meios_pagamentos(trimestre="20251", n_retornos="4")
ld.create_sqlite_table(meios_pag, "meios_pag", "pgs")
