from fpdf import FPDF


class PDF(FPDF):
    colontitle = None

    def header(self):
        """Оформление верхнего контитула каждого листа"""
        self.add_font(
            "DejaVuSans",
            fname="backend/font/DejaVuSans.ttf",
            uni=True)
        self.set_font("DejaVuSans", "", 14)
        width = self.get_string_width(self.colontitle) + 150
        self.set_x((210 - width) / 2)
        self.set_draw_color(0, 0, 0)
        self.set_fill_color(0, 80, 180)
        self.set_text_color(250, 250, 250)
        self.set_line_width(1)
        self.cell(width, 9, self.colontitle, 1, 1, "C", True)
        self.ln(10)

    def footer(self):
        # Нижний колонититул
        self.set_y(-15)
        self.set_font("helvetica", "I", 10)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


def get_pdf(ingredients):
    pdf = PDF(orientation="P", unit="mm", format="A4")
    pdf.colontitle = 'Hello'
    pdf.add_font("DejaVuSans", fname="backend/font/DejaVuSans.ttf", uni=True)
    pdf.add_page()
    pdf.set_left_margin(35)
    pdf.set_font("DejaVuSans", "", 14)
    for ingredient in ingredients:
        string = (ingredient['ingredient__name'] + ' - ' + str(
            ingredient['amount__sum']) + ' '
            + ingredient['ingredient__measurement_unit'])
        pdf.write(text=string)
        pdf.ln()
    pdf.output("test.pdf")
