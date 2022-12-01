"""This function write the analysis results.

"""


import xlsxwriter


class SaveLists:
    def __init__(self, xlsx_file, av_ints, bckg_vals):

        if xlsx_file[-4:] != "xlsx":
            xlsx_file  +=  ".xlsx"

        book    =  xlsxwriter.Workbook(xlsx_file)
        sheet1  =  book.add_worksheet("")
        sheet1.write(0, 0, "Frame")
        sheet1.write(0, 1, "Av Ints")
        sheet1.write(0, 2, "Bckg")
        sheet1.write(0, 3, "Ints / Bckg")

        for cnts, k in enumerate(av_ints):
            sheet1.write(cnts + 1, 0, cnts)
            sheet1.write(cnts + 1, 1, k)
            sheet1.write(cnts + 1, 2, bckg_vals[cnts])
            sheet1.write(cnts + 1, 3, k / bckg_vals[cnts])

        book.close()
