from datetime import datetime

template_sheet_id = 2112280131


def create_sheet_if_not_exist(sh, sheets_service):
    current_month = datetime.now().strftime('%B')
    current_year = datetime.now().strftime('%Y')
    sheet_name = current_month + " " + current_year

    sheet_list = sh.worksheets()
    names_list = []

    for lst in sheet_list:
        names_list.append(lst.title)

    if names_list.count(sheet_name) == 0:
        # Create worksheet from template
        copy_sheet_to_another_spreadsheet_request_body = {
            "destinationSpreadsheetId": sh.id
        }

        request = sheets_service.spreadsheets().sheets().copyTo(spreadsheetId=sh.id, sheetId=template_sheet_id,
                                                                body=copy_sheet_to_another_spreadsheet_request_body)

        response = request.execute()

        # Rename it
        body = {
            'requests': {"updateSheetProperties": {
                "properties": {
                    "sheetId": response.get("sheetId"),
                    "title": sheet_name,
                },
                "fields": "title"
            }
            }
        }

        response1 = sheets_service.spreadsheets().batchUpdate(spreadsheetId=sh.id, body=body).execute()

    worksheet = sh.worksheet(sheet_name)
    return worksheet


def add_transaction(t_type, t_date, t_sum, description, category, wsheet):
    date_cel = wsheet.find("Дата").col
    sum_cel = wsheet.find("Сумма").col
    desc_cel = wsheet.find("Описание").col
    category_cel = wsheet.find("Категория").col
    row_num = len(wsheet.col_values(date_cel)) + 1

    wsheet.update_cell(row_num, date_cel, t_date)
    wsheet.update_cell(row_num, sum_cel, t_sum)
    wsheet.update_cell(row_num, desc_cel, description)
    wsheet.update_cell(row_num, category_cel, category)

    if t_type == "+":
        income_cel = wsheet.find("Доходы").col
        income_category_cel = wsheet.find("Категория дохода").col
        row_num = len(wsheet.col_values(income_cel)) + 1
        wsheet.update_cell(row_num, income_cel, t_sum)
        wsheet.update_cell(row_num, income_category_cel, category)

    if t_type == "-":
        expense_cel = wsheet.find("Расходы").col
        expense_category_cel = wsheet.find("Категория расхода").col
        row_num = len(wsheet.col_values(expense_cel)) + 1
        wsheet.update_cell(row_num, expense_cel, t_sum)
        wsheet.update_cell(row_num, expense_category_cel, category)
