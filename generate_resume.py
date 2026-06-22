#!/usr/bin/env python3
"""Generate PDF resume for Alex Novotny.

Preferred method: open resume.html in a browser and print to PDF, or use
Playwright: page.pdf() with printBackground=true.

This script uses fpdf2 as a fallback when Playwright is unavailable.
"""

from fpdf import FPDF
from fpdf.enums import XPos, YPos

# --- Color constants (matches portfolio brand) ---
SIDEBAR_BG = (12, 16, 24)         # Deep navy sidebar
SIDEBAR_TEXT = (255, 255, 255)     # White
SIDEBAR_LABEL = (212, 168, 67)     # Gold labels
MAIN_BG = (250, 249, 246)          # Warm off-white
HEADING_COLOR = (184, 146, 47)     # Gold section headings
TEXT_COLOR = (26, 29, 36)          # Near black
SUBTEXT_COLOR = (92, 99, 112)      # Muted gray
BULLET_COLOR = (26, 29, 36)        # Body text
DIVIDER_COLOR = (228, 226, 220)    # Warm divider
SKILL_BG = (30, 36, 48)            # Skill pill background
NAME_COLOR = (26, 29, 36)          # Name color

# --- Layout constants ---
PAGE_W = 210
PAGE_H = 297
SIDEBAR_W = 62
MAIN_X = SIDEBAR_W + 6
MAIN_W = PAGE_W - MAIN_X - 8
SIDEBAR_PAD = 7

# Font paths (macOS system fonts)
FONT_REGULAR = "/System/Library/Fonts/HelveticaNeue.ttc"
FONT_BOLD = "/System/Library/Fonts/HelveticaNeue.ttc"

FONT_NAME = "HN"


class ResumePDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        # Register Unicode fonts
        self.add_font(FONT_NAME, "", FONT_REGULAR)
        self.add_font(FONT_NAME, "B", FONT_BOLD)
        # We'll use regular for italic since HelveticaNeue italic may not be in the .ttc
        self.add_font(FONT_NAME, "I", FONT_REGULAR)

    def header(self):
        # Draw sidebar background
        self.set_fill_color(*SIDEBAR_BG)
        self.rect(0, 0, SIDEBAR_W, PAGE_H, 'F')

    def footer(self):
        # Redraw sidebar to ensure it covers the full page
        self.set_fill_color(*SIDEBAR_BG)
        self.rect(0, 0, SIDEBAR_W, PAGE_H, 'F')


def set_font(pdf, style="", size=10):
    """Set font using our registered Unicode font."""
    pdf.set_font(FONT_NAME, style, size)


def nl_cell(pdf, w, h, text, **kwargs):
    """Cell that moves to next line."""
    pdf.cell(w, h, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT, **kwargs)


def add_sidebar_section_title(pdf, title, y):
    """Add a section title in the sidebar."""
    pdf.set_xy(SIDEBAR_PAD, y)
    set_font(pdf, "B", 10)
    pdf.set_text_color(*SIDEBAR_TEXT)
    pdf.cell(SIDEBAR_W - 2 * SIDEBAR_PAD, 5, title.upper(),
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    # Underline
    pdf.set_draw_color(100, 120, 145)
    pdf.set_line_width(0.3)
    pdf.line(SIDEBAR_PAD, y + 6, SIDEBAR_W - SIDEBAR_PAD, y + 6)
    return y + 10


def add_skill_item(pdf, skill, y):
    """Add a skill item with a subtle background pill."""
    pdf.set_xy(SIDEBAR_PAD, y)
    set_font(pdf, "", 8)
    # Draw pill background
    text_w = pdf.get_string_width(skill) + 6
    pdf.set_fill_color(*SKILL_BG)
    pdf.set_draw_color(*SKILL_BG)
    pill_h = 5.5
    pdf.rect(SIDEBAR_PAD, y, min(text_w, SIDEBAR_W - 2 * SIDEBAR_PAD), pill_h, 'F')
    pdf.set_xy(SIDEBAR_PAD + 3, y + 0.8)
    pdf.set_text_color(*SIDEBAR_TEXT)
    pdf.cell(SIDEBAR_W - 2 * SIDEBAR_PAD - 6, 4, skill)
    return y + pill_h + 2.5


def add_main_section_title(pdf, title):
    """Add a section heading in the main content area."""
    y = pdf.get_y()
    if y > PAGE_H - 30:
        pdf.add_page()
        y = 15

    pdf.set_xy(MAIN_X, y + 2)
    set_font(pdf, "B", 13)
    pdf.set_text_color(*HEADING_COLOR)
    pdf.cell(MAIN_W, 7, title.upper(), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    # Blue underline
    pdf.set_draw_color(*HEADING_COLOR)
    pdf.set_line_width(0.6)
    pdf.line(MAIN_X, y + 10, MAIN_X + MAIN_W, y + 10)
    pdf.set_xy(MAIN_X, y + 13)


def add_experience_header(pdf, company, role, dates, location=None):
    """Add company name, role, dates, and location."""
    y = pdf.get_y()
    if y > PAGE_H - 35:
        pdf.add_page()
        y = 15
        pdf.set_y(y)

    if company:
        pdf.set_x(MAIN_X)
        set_font(pdf, "B", 10.5)
        pdf.set_text_color(*TEXT_COLOR)
        pdf.cell(MAIN_W, 5.5, company, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_x(MAIN_X)
    set_font(pdf, "I", 9.5)
    pdf.set_text_color(*TEXT_COLOR)
    pdf.cell(MAIN_W, 5, role, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_x(MAIN_X)
    set_font(pdf, "", 8)
    pdf.set_text_color(*SUBTEXT_COLOR)
    date_loc = dates
    if location:
        date_loc += f"  |  {location}"
    pdf.cell(MAIN_W, 4.5, date_loc, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_xy(MAIN_X, pdf.get_y() + 1.5)


def add_description(pdf, text):
    """Add a description paragraph."""
    y = pdf.get_y()
    if y > PAGE_H - 20:
        pdf.add_page()
        pdf.set_y(15)

    pdf.set_x(MAIN_X)
    set_font(pdf, "", 8.5)
    pdf.set_text_color(*BULLET_COLOR)
    pdf.multi_cell(MAIN_W, 4, text)
    pdf.set_xy(MAIN_X, pdf.get_y() + 1)


def add_bullet(pdf, text):
    """Add a bullet point item."""
    y = pdf.get_y()
    if y > PAGE_H - 18:
        pdf.add_page()
        pdf.set_y(15)

    bullet_indent = 3
    set_font(pdf, "", 8.5)
    pdf.set_text_color(*BULLET_COLOR)

    # Bullet character (Unicode bullet works with TTF font)
    bullet_char = "\u2022  "
    bullet_w = pdf.get_string_width(bullet_char)
    text_x = MAIN_X + bullet_indent + bullet_w
    text_w = MAIN_W - bullet_indent - bullet_w

    # Print bullet
    pdf.set_xy(MAIN_X + bullet_indent, pdf.get_y())
    pdf.cell(bullet_w, 4, bullet_char)

    # Print text with wrapping
    pdf.set_xy(text_x, pdf.get_y())
    pdf.multi_cell(text_w, 4, text)

    pdf.set_xy(MAIN_X, pdf.get_y() + 0.5)


def build_sidebar_page1(pdf):
    """Build the sidebar content for page 1."""
    y = 45  # Start below the name area

    # --- Contact Section ---
    y = add_sidebar_section_title(pdf, "Contact", y)
    y += 2

    pdf.set_xy(SIDEBAR_PAD, y)
    set_font(pdf, "B", 7)
    pdf.set_text_color(*SIDEBAR_LABEL)
    pdf.cell(SIDEBAR_W - 2 * SIDEBAR_PAD, 4, "EMAIL",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    y = pdf.get_y()

    pdf.set_xy(SIDEBAR_PAD, y)
    set_font(pdf, "", 7)
    pdf.set_text_color(*SIDEBAR_TEXT)
    pdf.multi_cell(SIDEBAR_W - 2 * SIDEBAR_PAD, 3.5,
                   "alexanderrobertnovotny\n@gmail.com")
    y = pdf.get_y() + 4

    pdf.set_xy(SIDEBAR_PAD, y)
    set_font(pdf, "B", 7)
    pdf.set_text_color(*SIDEBAR_LABEL)
    pdf.cell(SIDEBAR_W - 2 * SIDEBAR_PAD, 4, "LINKEDIN",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    y = pdf.get_y()

    pdf.set_xy(SIDEBAR_PAD, y)
    set_font(pdf, "", 7)
    pdf.set_text_color(*SIDEBAR_TEXT)
    pdf.multi_cell(SIDEBAR_W - 2 * SIDEBAR_PAD, 3.5,
                   "www.linkedin.com/in/\nalex-robert-novotny")
    y = pdf.get_y() + 6

    # --- Top Skills Section ---
    y = add_sidebar_section_title(pdf, "Top Skills", y)
    y += 3
    skills = ["Video Production", "Public Relations", "Python (Programming\nLanguage)"]
    for skill in skills:
        y = add_skill_item(pdf, skill, y)

    return y


def generate_resume():
    pdf = ResumePDF()
    pdf.set_margin(0)
    pdf.add_page()

    # =========================================================
    # PAGE 1 - SIDEBAR
    # =========================================================
    build_sidebar_page1(pdf)

    # =========================================================
    # PAGE 1 - MAIN CONTENT - NAME & TITLE
    # =========================================================
    pdf.set_xy(MAIN_X, 12)
    set_font(pdf, "B", 24)
    pdf.set_text_color(*NAME_COLOR)
    pdf.cell(MAIN_W, 10, "Alex Novotny", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_x(MAIN_X)
    set_font(pdf, "", 11)
    pdf.set_text_color(*SUBTEXT_COLOR)
    pdf.cell(MAIN_W, 6, "Head of Developer Relations & Marketing at Massive",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_x(MAIN_X)
    set_font(pdf, "", 9)
    pdf.set_text_color(*SUBTEXT_COLOR)
    pdf.cell(MAIN_W, 5, "Austin, Texas Metropolitan Area",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Thin divider under name block
    pdf.set_draw_color(*DIVIDER_COLOR)
    pdf.set_line_width(0.3)
    div_y = pdf.get_y() + 3
    pdf.line(MAIN_X, div_y, MAIN_X + MAIN_W, div_y)
    pdf.set_xy(MAIN_X, div_y + 4)

    # =========================================================
    # EXPERIENCE SECTION
    # =========================================================
    add_main_section_title(pdf, "Experience")
    pdf.set_xy(MAIN_X, pdf.get_y() + 3)

    # --- Massive ---
    add_experience_header(pdf, "Massive", "Head of Developer Relations & Marketing",
                          "June 2025 - Present (9 months)", "Austin, TX")
    add_description(pdf,
        "Kickstarted developer relations at Massive from scratch by leading a small team, "
        "executing multiple marketing campaigns, and serving as the internal voice of the "
        "developer. Contributed millions of impressions across social channels to increase "
        "brand awareness. Influenced customer conversions from free to paid.")

    massive_bullets = [
        "Led the developer relations function",
        "Led all marketing efforts across the company",
        "Oversaw the planning and completion of our company rebrand from Polygon.io to Massive.com",
        "Completed multiple Public Relations initiatives with NYSE, Nasdaq, TMX, ETF Global and Benzinga",
        "Independently created demos, wrote blogs, recorded videos, and managed social media channels",
        "Interviewed developers about pain points and took that feedback to engineering",
    ]
    for b in massive_bullets:
        add_bullet(pdf, b)

    pdf.set_xy(MAIN_X, pdf.get_y() + 4)

    # --- Box ---
    pdf.set_x(MAIN_X)
    set_font(pdf, "B", 10.5)
    pdf.set_text_color(*TEXT_COLOR)
    pdf.cell(MAIN_W, 5.5, "Box", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_x(MAIN_X)
    set_font(pdf, "", 8)
    pdf.set_text_color(*SUBTEXT_COLOR)
    pdf.cell(MAIN_W, 4.5, "5 years 9 months", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_xy(MAIN_X, pdf.get_y() + 2)

    # Senior Developer Advocate
    add_experience_header(pdf, "", "Senior Developer Advocate",
                          "April 2023 - June 2025 (2 years 3 months)", "Austin, Texas")
    add_description(pdf,
        "Taught developers Box APIs and AI through various developer relations activities, "
        "including blogs, videos, sample code, and live demos, while serving as a team mentor and lead.")

    sda_bullets = [
        "Served as our developer relations social media manager, posting everyday on multiple platforms, gathering 100s of thousands of impressions, reposts, and likes",
        "Created content, enhancements, and sample code alongside at least 10 major AI partners, including but not limited to OpenAI, Google, Weaviate, Pinecone, and Salesforce",
        "Coded multiple RAG Agentic workflow demos, using Box as the content storage location",
        "Helped code the Box developer MCP server",
        "Wrote, recorded, and launched a new YouTube video series on the new Box AI API, now with over 5000 views",
        "Wrote 35 Medium blogs garnering over 9,500 views",
        "Attended conferences like Google Next, Salesforce TDX, Box Works and Langchain Interrupt, working the booth and speaking live with 100s of developers",
        "Created and recorded multiple remote sessions for Box virtual events, like Cloud Content Summit and Box Works",
    ]
    for b in sda_bullets:
        add_bullet(pdf, b)

    pdf.set_xy(MAIN_X, pdf.get_y() + 4)

    # Developer Evangelist II
    add_experience_header(pdf, "", "Developer Evangelist II",
                          "April 2021 - April 2023 (2 years 1 month)", "Austin, Texas")
    add_description(pdf,
        "Taught developers Box APIs through various developer relations activities, "
        "including documentation, blogs, videos, sample code, and live demos.")

    de2_bullets = [
        "Served as the interim Box developer relations lead for six months after company attrition",
        "Conducted over 25 interviews to expand the team",
        "Wrote over 15 medium blog posts with over 5000 views",
        "Helped plan our team's first public Hackathon, as well as mentored the three teams on technical questions",
        "Created and presented a developer relations strategy and expansion plan to upper leadership",
        "Wrote, recorded, and launched a new YouTube video series on Box API topics, now with over 3000 views",
        "Responded to over 1000 developer questions on the Box Platform community forum",
        "Served as the SME for Box Skills in over 10 customer calls",
        "Coded over 200 documentation releases on developer.box.com visited by over 40,000 people a month",
        "Created a ChatGPT demo and presented the solution to the C-suite",
    ]
    for b in de2_bullets:
        add_bullet(pdf, b)

    pdf.set_xy(MAIN_X, pdf.get_y() + 4)

    # Technical Consultant
    add_experience_header(pdf, "", "Technical Consultant",
                          "October 2019 - April 2021 (1 year 7 months)", "Austin, Texas")
    add_description(pdf,
        "Led or participated in over 75 Box Consulting engagements, including API Enablement, "
        "SSO, Shuttle, Transform, Shield, Keysafe, Integration, Enterprise ID Merge, and User Analysis projects.")

    tc_bullets = [
        "Worked with peers to create a scalable small business administration loan application integration with Box for the first Covid-19 government stimulus package",
        "Developed and presented a repeatable developer enablement flow based around the Box CLI",
        "Used the Box Salesforce SDK to create custom folders programmatically for customers",
        "Sold 10+ phase 2 Box Consulting engagements totaling over $100,000 in revenue",
        "Co-led the Content Migration Best Practices Box Works 2020 presentation",
    ]
    for b in tc_bullets:
        add_bullet(pdf, b)

    pdf.set_xy(MAIN_X, pdf.get_y() + 4)

    # --- Texas Education Agency ---
    add_experience_header(pdf, "Texas Education Agency", "Tools Administrator (Programmer V)",
                          "April 2019 - October 2019 (7 months)", "Austin, Texas")
    add_description(pdf,
        "Technical lead responsible for the installation, configuration, and upgrades of "
        "Jira, Zendesk, Qualtrics, Azure DevOps, Ipswitch, Teamforge, and ArcGIS.")

    tea_bullets = [
        "Saved the agency over $100,000 by creating an excel macro to meet a short three month legislative deadline",
        "Coded python scripts to migrate data between instances for reporting purposes using Zendesk's REST API",
    ]
    for b in tea_bullets:
        add_bullet(pdf, b)

    pdf.set_xy(MAIN_X, pdf.get_y() + 4)

    # --- Google ---
    add_experience_header(pdf, "Google", "Tools Administrator (TVC)",
                          "October 2018 - April 2019 (7 months)", "Austin, Texas")
    add_description(pdf,
        "Managed a suite of Google Shopping applications, overseeing the full project life cycle, "
        "and communicated daily with stakeholders to advance application roadmaps and gather "
        "requirements from a wide range of Google users.")

    google_bullets = [
        "Investigated bugs for over 10 tools and worked directly with engineering to create action plans to address them",
        "Streamlined metric monitoring and used Google PLX to implement dashboards allowing users to track success down to the granular level of a ticket",
    ]
    for b in google_bullets:
        add_bullet(pdf, b)

    pdf.set_xy(MAIN_X, pdf.get_y() + 4)

    # --- Koch Industries ---
    add_experience_header(pdf, "Koch Industries", "Software Developer",
                          "October 2016 - September 2018 (2 years)", "Wichita, Kansas")
    add_description(pdf,
        "Primary support developer for over 15 applications. Investigated and solved hundreds "
        "of bugs using the .Net stack. Led a team of 10 in university IT recruitment.")

    koch_bullets = [
        "Migrated 5 applications to AWS which included creating EC2 instances, S3 buckets, load balancers, DNS management, other database upgrades",
        "Migrated over 10 ETL integrations from our legacy integration tool called Informatica to Dell Boomi and mentored interns on cloud based technology",
    ]
    for b in koch_bullets:
        add_bullet(pdf, b)

    pdf.set_xy(MAIN_X, pdf.get_y() + 4)

    # --- Quorum Software ---
    add_experience_header(pdf, "Quorum Software", "Software Developer",
                          "June 2015 - September 2016 (1 year 4 months)", "Dallas, Texas")
    add_description(pdf,
        "Primary support developer for over 5 applications and 50 clients, while serving as a "
        "technical liaison to clients and participating in university IT recruiting efforts.")

    quorum_bullets = [
        "Collaborated with team to code an integration solution in C# that moves data between land systems and an oil revenue allocation processor",
        "Provided on site support by creating SQL scripts to convert data to Quorum software",
    ]
    for b in quorum_bullets:
        add_bullet(pdf, b)

    pdf.set_xy(MAIN_X, pdf.get_y() + 6)

    # =========================================================
    # EDUCATION SECTION
    # =========================================================
    add_main_section_title(pdf, "Education")
    pdf.set_xy(MAIN_X, pdf.get_y() + 3)

    # Oklahoma State University
    pdf.set_x(MAIN_X)
    set_font(pdf, "B", 10)
    pdf.set_text_color(*TEXT_COLOR)
    pdf.cell(MAIN_W, 5.5, "Oklahoma State University",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_x(MAIN_X)
    set_font(pdf, "", 9)
    pdf.set_text_color(*SUBTEXT_COLOR)
    pdf.cell(MAIN_W, 5, "Master of Business Administration (MBA)",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_xy(MAIN_X, pdf.get_y() + 3)

    # Southern Arkansas University
    pdf.set_x(MAIN_X)
    set_font(pdf, "B", 10)
    pdf.set_text_color(*TEXT_COLOR)
    pdf.cell(MAIN_W, 5.5, "Southern Arkansas University",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_x(MAIN_X)
    set_font(pdf, "", 9)
    pdf.set_text_color(*SUBTEXT_COLOR)
    pdf.cell(MAIN_W, 5, "Bachelor of Arts (BA), Theatre/Theater",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # =========================================================
    # OUTPUT
    # =========================================================
    output_path = "/Users/alexnovotny/Desktop/smartoneinok.portfolio.io/AlexNovotnyResume.pdf"
    pdf.output(output_path)
    print(f"Resume generated successfully: {output_path}")
    print(f"Total pages: {pdf.pages_count}")


if __name__ == "__main__":
    generate_resume()
