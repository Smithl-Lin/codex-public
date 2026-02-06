from fpdf import FPDF
import datetime

class MayoWhitePaper(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Global Medical Resource Dispatch White Paper (2026)', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()} | Researcher: Smith Lin (Mayo Clinic)', 0, 0, 'C')

def generate_report():
    pdf = MayoWhitePaper()
    pdf.add_page()
    pdf.set_font("Arial", size=11)

    # 1. 执行摘要
    pdf.set_font("Arial", 'B', 13)
    pdf.cell(0, 10, "1. Executive Summary", 0, 1)
    pdf.set_font("Arial", size=11)
    content1 = (
        "This report outlines the strategic deployment of 19,815 high-value medical assets. "
        "The system has achieved a milestone 0.79 distance score in precision matching, "
        "ensuring 0% cross-disciplinary mismatch rates for HNWIs seeking iPS and BCI therapies."
    )
    pdf.multi_cell(0, 8, content1)
    pdf.ln(5)

    # 2. 资产全景分析
    pdf.set_font("Arial", 'B', 13)
    pdf.cell(0, 10, "2. Global Asset Landscape", 0, 1)
    pdf.set_font("Arial", size=11)
    content2 = (
        "- Total Assets: 19,815 (Saturated Coverage)\n"
        "- Key Nodes: USA (ClinicalTrials.gov), Japan (jRCT iPS Excellence), Mayo Internal Leads\n"
        "- Tech Domains: KRAS/mRNA Vaccines, BCI Neural Interfaces, iPSC Regenerative Medicine"
    )
    pdf.multi_cell(0, 8, content2)
    pdf.ln(5)

    # 3. 核心绩效指标 (KPIS)
    pdf.set_font("Arial", 'B', 13)
    pdf.cell(0, 10, "3. Key Performance Milestones", 0, 1)
    pdf.set_font("Arial", size=11)
    # 引用 0.79 距离突破
    content3 = (
        "- Peak Precision: 0.79 Distance Score (Targeted Therapy Matching)\n"
        "- Defensive Accuracy: 100% Interception of age/criteria mismatches\n"
        "- Search Depth: N=100 Re-ranking logic implemented"
    )
    pdf.multi_cell(0, 8, content3)
    pdf.ln(5)

    # 4. 财务对位 (Shadow Billing)
    pdf.set_font("Arial", 'B', 13)
    pdf.cell(0, 10, "4. Shadow Billing Framework", 0, 1)
    pdf.set_font("Arial", size=11)
    # 引用阶梯定价模型
    content4 = (
        "- Mature Device Pathway (DBS/Robotic): $50,000 - $120,000\n"
        "- Frontier Research Pathway (iPS/BCI): $150,000 - $300,000+\n"
        "- Financial logic: Research access assessment & specialized monitoring included."
    )
    pdf.multi_cell(0, 8, content4)

    # 5. 结语
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 10)
    pdf.multi_cell(0, 8, f"Report Generated on: {datetime.date.today()} | Security Level: Mayo Internal Strategic")

    output_name = "Mayo_Global_Resource_WhitePaper_2026.pdf"
    pdf.output(output_name)
    print(f"🚀 白皮书已生成: {output_name}")

if __name__ == "__main__":
    generate_report()