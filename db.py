import sqlite3

income_categories = {"зарплата": ["зп", "премия", "отпускные"],
                     "переводы": ["перевод"],
                     "возврат долга": ["долг"]}

expense_categories = {"транспорт": ["метро", "такси", "автобус"],
                      "еда": ["продукты", "перекус", "столовая"],
                      "развлечения": ["кино", "кафе", "бар", "ресторан", "театр", "музей", "балет", "филармония",
                                      "алкоголь", "табак"],
                      "связь": ["интернет", "телефон"],
                      "праздники": ["подарок", "подарки"],
                      "здоровье": ["аптека", "стоматология", "медицина"],
                      "красота": ["косметика", "парикмахер"],
                      "одежда и обувь": ["одежда", "обувь", "белье"],
                      "дом": ["мебель", "техника", "быт", "дом"],
                      "зоотовары": ["корм", "наполнитель", "мартин"],
                      "квартплата": ["аренда", "жкх", "квартплата"],
                      "хобби": ["книги"],
                      "налоги": ["налог", "пошлина"]}


def init_database():
    connection = sqlite3.connect("categories.db")
    cursor = connection.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS categories
                      (
                        ctg_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        name text [ NOT NULL ] UNIQUE, 
                        parent_ctg_id integer [ NULL ],
                        type text [NOT NULL],
                        CONSTRAINT fk_ctg_id
                        FOREIGN KEY (ctg_id)
                        REFERENCES categories(ctg_id)
                      )                   
                   """)

    # Add default categories
    for main_ctg in expense_categories.keys():
        cursor.execute("INSERT OR IGNORE INTO categories (name, parent_ctg_id, type) VALUES (?, ?, 'out')", (main_ctg, None))
        for ctg in expense_categories.get(main_ctg):
            cursor.execute("INSERT OR IGNORE INTO categories (name, parent_ctg_id, type) VALUES "
                               "(?, (select ctg_id from categories where name=?), 'out')", (ctg, main_ctg))

    for main_ctg in income_categories.keys():
        cursor.execute("INSERT OR IGNORE INTO categories (name, parent_ctg_id, type) VALUES (?, ?, 'in')", (main_ctg, None))
        for ctg in income_categories.get(main_ctg):
            cursor.execute("INSERT OR IGNORE INTO categories (name, parent_ctg_id, type) VALUES "
                               "(?, (select ctg_id from categories where name=?), 'out')", (ctg, main_ctg))

    connection.commit()
    connection.close()
