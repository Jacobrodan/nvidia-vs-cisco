import json
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, KeepTogether
from reportlab.lib.utils import ImageReader
from model import MARKET_CAP, REV_TTM

R = json.load(open("results.json"))
pc = lambda x, d=0: f"{100*x:.{d}f}%"
bn = lambda x: f"${x/1e9:,.0f} billion"

body = ParagraphStyle("b", fontName="Times-Roman", fontSize=10, leading=12.9, alignment=TA_JUSTIFY, spaceAfter=4.5)
h1 = ParagraphStyle("h", fontName="Times-Bold", fontSize=11, leading=14, spaceBefore=7, spaceAfter=2.5, keepWithNext=1)
title = ParagraphStyle("t", fontName="Times-Bold", fontSize=17, leading=21, alignment=TA_CENTER, spaceAfter=5)
sub = ParagraphStyle("s", fontName="Times-Italic", fontSize=11.5, leading=14, alignment=TA_CENTER, spaceAfter=6)
auth = ParagraphStyle("a", fontName="Times-Roman", fontSize=10.5, leading=13, alignment=TA_CENTER)
absb = ParagraphStyle("ab", fontName="Times-Roman", fontSize=9.4, leading=12, alignment=TA_JUSTIFY)
cap = ParagraphStyle("c", fontName="Times-Roman", fontSize=8.6, leading=10.6, alignment=TA_JUSTIFY, spaceAfter=7)
ref = ParagraphStyle("r", fontName="Times-Roman", fontSize=8.5, leading=10.5, leftIndent=12, firstLineIndent=-12, spaceAfter=1.5)
cell = ParagraphStyle("cell", fontName="Times-Roman", fontSize=8.8, leading=10.5)
W = 6.7 * inch

def img(p, w=W):
    iw, ih = ImageReader(p).getSize(); return Image(p, width=w, height=w * ih / iw)

def eq(p, num, w_in):
    iw, ih = ImageReader(p).getSize()
    t = Table([["", Image(p, width=w_in * inch, height=w_in * inch * ih / iw),
                Paragraph(f"({num})", ParagraphStyle("n", fontName="Times-Roman", fontSize=10, alignment=2))]],
              colWidths=[0.4 * inch, W - 0.8 * inch, 0.4 * inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ALIGN", (1, 0), (1, 0), "CENTER")])); return t

def booktabs(rows, widths, bold_first_col=False):
    data = [[Paragraph(str(c), ParagraphStyle("x", parent=cell, fontName="Times-Bold" if i == 0 else "Times-Roman")) for c in r]
            for i, r in enumerate(rows)]
    t = Table(data, colWidths=widths)
    t.setStyle(TableStyle([("LINEABOVE", (0, 0), (-1, 0), 1, colors.black), ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.black),
                           ("LINEBELOW", (0, -1), (-1, -1), 1, colors.black), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
    return t

S = []
S += [Paragraph("Is Nvidia the Next Cisco?", title),
      Paragraph("A Monte Carlo test of the AI trade", sub),
      Paragraph("Jacob Rodan<br/><font size=9.5>September 2026</font><br/><font size=9>github.com/Jacobrodan/nvidia-vs-cisco</font>", auth), Spacer(1, 9)]

abstract = (
    f"<b>Abstract.</b> In March 2000, Cisco was the most valuable company in the world and the company selling the picks and "
    f"shovels of the internet. Its business kept growing, yet its stock took more than 25 years to recover. Nvidia now holds the "
    f"same position in artificial intelligence. I ask whether an investor buying Nvidia today faces the same risk. I first argue "
    f"both sides using public filings, then simulate 100,000 five-year futures for Nvidia's revenue, profit margin and valuation, "
    f"including the chance of a sudden AI spending bust like the one that hit Cisco in 2001. The median outcome is a "
    f"{pc(R['median'],1)} annual return, with a {pc(R['p_loss'])} chance of losing money and a {pc(R['p10'])} chance of beating 10% a year. "
    f"The result splits cleanly in two: futures without a spending bust return a median {pc(R['med_nobust'])} a year, futures with one "
    f"return {pc(R['med_bust'])}. Nvidia is not priced like Cisco was. Its risk is Cisco's cycle, not Cisco's price.")
at = Table([[Paragraph(abstract, absb)]], colWidths=[W - 0.5 * inch])
at.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#888888")), ("LEFTPADDING", (0, 0), (-1, -1), 9),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 9), ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
S += [at, Spacer(1, 4)]

S.append(Paragraph("1. The question", h1))
S.append(Paragraph(
    "Every technology boom has a company that sells the equipment everyone else needs. In the internet boom it was Cisco. On "
    "March 27, 2000 its stock closed at $80.06 and it briefly became the world's most valuable company. Its revenue then roughly "
    "quintupled over the following decades, and its stock still did not pass that price again until December 2025. The company "
    "was right about the internet. The people who bought it at the top were wrong about the price.", body))
S.append(Paragraph(
    f"Nvidia is today's version of that company. It is worth about $5.4 trillion and sold {bn(REV_TTM)} of products over its last "
    "four quarters. The obvious question is whether it is heading for the same ending. This paper tries to answer it with numbers "
    "instead of opinions: first by arguing both sides, then by simulating what has to happen for an investor who buys today to do well.", body))

S.append(Paragraph("2. The case that Nvidia is the next Cisco", h1))
S.append(Paragraph(
    "The strongest argument is not about valuation. It is about who the customers are. Cisco sold to telecom companies and internet "
    "startups that were building networks with borrowed and newly raised money. When that money stopped, orders stopped with it. "
    "In its third quarter of fiscal 2001, Cisco reported \"a sudden and significant decrease in demand\" for its products, only a year "
    "after growing sales 55%. Nvidia's revenue depends on a small group of very large customers building data centers as fast as they "
    "can. That spending only continues if those customers keep believing AI will pay them back.", body))
S.append(Paragraph(
    "Nvidia has also been through this before. In fiscal 2023, after the crypto and pandemic demand faded, its revenue went flat and "
    "its stock fell by roughly two-thirds from its late 2021 high. Chip companies are cyclical. A company earning 56% net margins "
    "will attract competitors, including its own customers designing their own chips. Margins that high rarely last.", body))

S.append(Paragraph("3. The case that it is not", h1))
S.append(Paragraph(
    "The strongest argument on the other side is simple: Cisco was expensive in a way Nvidia is not. At its peak Cisco traded above "
    "200 times earnings. Nvidia trades around 28 times. Cisco kept 14 cents of every dollar of revenue as profit, Nvidia keeps about "
    "56. And Nvidia's growth is faster, not slower: its most recent quarter was up 106% from a year earlier. One quarter of Nvidia's "
    "revenue is now about five times Cisco's revenue for its entire peak year.", body))
t1 = booktabs([
    ["", "Cisco, March 2000", "Nvidia, September 2026"],
    ["Price to earnings", "Above 200x", "About 28x"],
    ["Price to sales", "About 31-39x", f"About {MARKET_CAP/REV_TTM:.0f}x (trailing four quarters)"],
    ["Latest annual revenue", "$18.9 billion (FY2000)", "$215.9 billion (FY2026)"],
    ["Revenue growth", "+55% (FY2000)", "+65% (FY2026); +106% latest quarter"],
    ["Net profit margin", "14% (FY2000)", "56% (FY2026)"],
], [1.6 * inch, 2.1 * inch, 3.0 * inch])
S.append(KeepTogether([Paragraph("<b>Table 1.</b> The two companies at the moment of the comparison. Sources: company filings; "
                                 "market data and press reports listed in the references.", cap), t1]))
S.append(Spacer(1, 6))
S.append(Paragraph(
    "So the two sides disagree about different things. The bear case is about whether the demand lasts. The bull case is about "
    "whether the price is reasonable if it does. A useful test has to include both.", body))

S.append(Paragraph("4. The model", h1))
S.append(Paragraph(
    "I simulate Nvidia's revenue one quarter at a time for five years, starting from its most recent quarter. In normal years growth "
    "starts high and fades each year toward a long-run rate of 4%. In any given year there is a chance of an AI spending bust, in "
    "which revenue falls by 20% to 50% over two quarters, the way Cisco's did. Revenue R in year t follows", body))
S.append(eq("eq1.png", 1, 5.6))
S.append(Paragraph(
    "where g<sub>1</sub> is next year's growth, &#961; is how fast growth fades and b<sub>t</sub> is the size of a bust. After five "
    "years, the company's value is its revenue times a profit margin m times a price-to-earnings multiple, plus about 1% a year from "
    "share buybacks. The annual return r compares that value to today's $5.43 trillion:", body))
S.append(eq("eq2.png", 2, 4.6))
t2 = booktabs([
    ["Input", "Range used", "Why"],
    ["Next-year growth, g<sub>1</sub>", "35% average (sd 15%)", "Latest quarter grew 106%; sequential growth near 18% a quarter"],
    ["Fade rate, &#961;", "0.45 to 0.80 per year", "Fast-growing companies keep only part of their growth each year"],
    ["Chance of a bust", "12% per year", "Chip demand has historically turned down every few years"],
    ["Size of a bust", "20% to 50% of revenue", "Nvidia FY2023 was flat; Cisco fell sharply in 2001"],
    ["Net margin in 2031", "35% to 55%", "Today 56%; competition should pull it down"],
    ["P/E in 2031", "15x to 35x", "Range for large, mature technology companies"],
], [1.55 * inch, 1.55 * inch, 3.6 * inch])
S.append(KeepTogether([Paragraph("<b>Table 2.</b> Model inputs. Each simulation draws every input at random from these ranges.", cap), t2]))
S.append(Spacer(1, 6))
S.append(Paragraph(
    "None of these ranges is a prediction. They are my best attempt at a fair set of possibilities, and the code lets anyone "
    "change them. I set them before running the simulation and did not adjust them after seeing the results. The one I am least sure "
    "about is the chance of a bust, so instead of defending a single number, Figure 2b shows how the answer changes across the whole range.", body))

S.append(Paragraph("5. Results", h1))
S.append(Paragraph(
    f"The median simulated revenue in 2031 is {bn(R['rev5'])}, roughly double today. To break even at a normal mature valuation, "
    f"Nvidia needs about {bn(R['need0'])}. To return 10% a year it needs about {bn(R['need10'])}. Figure 1 shows most futures clearing "
    f"the first line and a minority clearing the second.", body))
S.append(KeepTogether([img("fig1.png"), Paragraph(
    "<b>Figure 1.</b> 1,000 of the 100,000 simulated revenue paths. Dashed lines show the revenue Nvidia would need in 2031 to "
    "break even (black) or return 10% a year (red), assuming a 45% margin and a 25x P/E.", cap)]))
t3 = booktabs([
    ["Outcome over five years", "Share of simulations"],
    ["Median annual return", pc(R["median"], 1)],
    ["Lose money", pc(R["p_loss"])],
    ["Return more than 10% a year", pc(R["p10"])],
    ["Return more than 20% a year", pc(R["p20"])],
    ["Lose half or more, a Cisco-style outcome", pc(R["p_half"], 1)],
    ["At least one AI spending bust", pc(R["bust_share"])],
], [3.6 * inch, 1.6 * inch])
S.append(KeepTogether([Paragraph("<b>Table 3.</b> Results across 100,000 simulations.", cap), t3]))
S.append(Spacer(1, 6))
S.append(Paragraph(
    f"The most useful result is that the outcomes split into two groups. When no bust happens, the median return is "
    f"{pc(R['med_nobust'])} a year, close to what the stock market has returned over long periods. When at least one bust happens, the "
    f"median return is {pc(R['med_bust'])}. Figure 2b turns this into one number: the median return reaches 10% a year only if the "
    f"chance of a bust is below about {pc(R['breakeven_bust'],1)} a year. In other words, today's price already assumes the spending "
    f"cycle is unusually safe.", body))
S.append(KeepTogether([img("fig2.png"), Paragraph(
    "<b>Figure 2.</b> (a) Annual returns in futures with and without an AI spending bust. (b) Median annual return as the yearly "
    "chance of a bust changes; the dotted line marks where the median falls below 10%.", cap)]))
S.append(Paragraph(
    "Figure 3 ranks which inputs matter most. Next year's growth, the final P/E multiple and the chance of a bust each move the median "
    "return by roughly 12 to 19 percentage points between their best and worst cases. Profit margins and the speed of the fade matter "
    "less. Every input near the top is really a question about one thing: how long AI spending keeps growing.", body))
S.append(KeepTogether([img("fig3.png"), Paragraph(
    "<b>Figure 3.</b> Median annual return when each input is in its worst 10% versus its best 10% of draws. The vertical line is the "
    "overall median.", cap)]))

S.append(Paragraph("6. Verdict", h1))
S.append(Paragraph(
    "On price, Nvidia is not the next Cisco. Cisco needed a miracle to justify its valuation in 2000. Nvidia needs something much more "
    "ordinary: for its revenue to roughly double over five years and for its margins to hold up reasonably well. Most of the simulated "
    "futures deliver that.", body))
S.append(Paragraph(
    "On the cycle, it could be. The model says the main way an investor loses money here is not that the stock was absurdly expensive. "
    "It is that the customers stop buying for a year or two, the way Cisco's did in 2001. Whether that happens depends less on Nvidia "
    "than on whether the companies buying its chips earn enough from AI to keep spending.", body))
S.append(Paragraph(
    "The most useful thing to track is therefore not Nvidia's own earnings. It is how much its largest "
    "customers make from AI compared with how much they spend on it. As long as that gap keeps closing, the boom has a floor. If it "
    "stops closing, the Cisco comparison starts to look much closer.", body))

S.append(Paragraph("7. Limitations", h1))
S.append(Paragraph(
    "The input ranges are judgments, and different reasonable ranges give different answers; the code is written so they can be "
    "changed in one place. The model ignores interest rates, taxes on buybacks, dividends and dilution from stock compensation. Busts "
    "are treated as independent from year to year, while real downturns can cluster. Five years is one horizon among many. This is "
    "a model of what has to be true, not a forecast, and not investment advice.", body))

S.append(Paragraph("References", h1))
for rt in [
    "Cisco Systems (2000). Fiscal 2000 results, Form 8-K; (2001) Annual Report, Form 10-K; (2001) Quarterly Report for Q3 fiscal 2001, Form 10-Q. U.S. SEC.",
    "Glasserman, P. (2003). <i>Monte Carlo Methods in Financial Engineering</i>. Springer.",
    "NVIDIA Corporation (2026). Fiscal 2026 Annual Report, Form 10-K; results for Q1 and Q2 fiscal 2027, Forms 8-K. U.S. SEC.",
    "Perez, C. (2002). <i>Technological Revolutions and Financial Capital: The Dynamics of Bubbles and Golden Ages</i>. Edward Elgar.",
    "Market data: NVIDIA market capitalization, stockanalysis.com (September 25, 2026); price and P/E, Robinhood (September 26, 2026).",
    "Cisco valuation at the 2000 peak: Slashdot, \"Cisco stock hits new all-time high, 25 years after the dotcom bubble burst\" (December 11, 2025); YCharts data via C. Bilello (2020).",
]:
    S.append(Paragraph(rt, ref))
S.append(Spacer(1, 4))
S.append(Paragraph("<i>Code and data: github.com/Jacobrodan/nvidia-vs-cisco. Comments and corrections are welcome.</i>", cap))

def on_page(c, d):
    c.saveState(); c.setFont("Times-Roman", 8.5); c.drawCentredString(letter[0] / 2, 0.45 * inch, str(d.page)); c.restoreState()

doc = SimpleDocTemplate("Is_Nvidia_the_Next_Cisco.pdf", pagesize=letter, leftMargin=0.9 * inch, rightMargin=0.9 * inch,
                        topMargin=0.7 * inch, bottomMargin=0.7 * inch, title="Is Nvidia the Next Cisco?", author="Jacob Rodan")
doc.build(S, onFirstPage=on_page, onLaterPages=on_page)
print("ok")
