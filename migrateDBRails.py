import lib.handle_db as dbh

print("Migrate DB for rails app")

#table_mappings={"articles":"articles", "affiliations":"affiliations", "affiliation_addresses":"addresses", "Authors":"authors", "Themes":"Themes", "Article_Theme_links":"Article_Themes", "Article_author_links":"article_authors", "affiliation_links":"affiliation_links"}

table_mappings={"Article_author_links":"article_authors", "affiliation_links":"affiliation_links"}

source_db = dbh.DataBaseAdapter('ukch_articles.sqlite')
target_db = dbh.DataBaseAdapter('../railsapp/ukcatalysishub/db/development.sqlite3')


for tm in table_mappings:
    print("Migrating from", tm, "to", table_mappings[tm])

    articles = source_db.get_full_table(tm)
    articles_info = source_db.get_table_info(tm)

    print(tm, "table records:", len(articles),"fields", len(articles_info))

    art_fields =[]
    for fn in articles_info:
        art_fields.append(fn[1])
    # for rails need to add created_at and updated_at fields
    art_fields.append('created_at')
    art_fields.append('updated_at')

    for article in articles:
        article = article + ('2020-02-12','2020-02-12')
        columns = str(tuple(art_fields)).replace("'", "")
        values = str(tuple(article))
        print("INSERT INTO articles %s VALUES %s " % (columns, values))
        target_db.put_values_table(table_mappings[tm], art_fields, article)
    

