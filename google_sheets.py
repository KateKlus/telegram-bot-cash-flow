from datetime import datetime


def create_sheet_if_not_exist(sh):
    current_month = datetime.now().strftime('%B')
    current_year = datetime.now().strftime('%Y')
    sheet_name = current_month + " " + current_year

    sheet_list = sh.worksheets()
    names_list = []

    for lst in sheet_list:
        names_list.append(lst.title)

    if names_list.count(sheet_name) == 0:
        sh.add_worksheet(title=sheet_name, rows="100", cols="11")

    worksheet = sh.worksheet(sheet_name)
    return worksheet


def add_transaction(t_type, t_date, t_sum, description, category, wsheet):
    date_cel = wsheet.find("Дата").col
    sum_cel = wsheet.find("Сумма").col
    desc_cel = wsheet.find("Описание").col
    category_cel = wsheet.find("Категория").col
    row_num = len(wsheet.col_values(wsheet.find("Дата").col)) + 1

    wsheet.update_cell(row_num, date_cel, t_date)
    wsheet.update_cell(row_num, sum_cel, t_sum)
    wsheet.update_cell(row_num, desc_cel, description)
    wsheet.update_cell(row_num, category_cel, category)
