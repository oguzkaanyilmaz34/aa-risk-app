import math
import gradio as gr

# --- MODEL KATSAYILARI (senin verinden hesaplananlar) ---
B0 = 0.030165
B_CRT_0p1 = 0.032975
B_ASO10 = 0.091883
B_FEMALE = -1.041297
B_AI_ABSENCE = -2.348336
B_ANTI_TPO = 0.844441

def predict_probability(crt_value, crt_unit, aso10, cinsiyet, ai_hastalik, antitpo):
    try:
        crt_val = float(crt_value)
    except:
        return "Geçersiz Calreticulin değeri", None

    crt_ug_ml = crt_val / 1000.0 if crt_unit == "ng/mL" else crt_val
    crt_per_0p1 = crt_ug_ml / 0.1
    female = 1 if cinsiyet == "K" else 0
    ai_absence = 1 if ai_hastalik == "Yok" else 0
    anti_tpo_high = 1 if antitpo == "Yüksek" else 0

    logit_p = (B0 + B_CRT_0p1 * crt_per_0p1 + B_ASO10 * float(aso10)
               + B_FEMALE * female + B_AI_ABSENCE * ai_absence + B_ANTI_TPO * anti_tpo_high)
    p = 1 / (1 + math.exp(-logit_p))
    pct = round(p * 100, 1)

    yorum = ("Düşük" if p < 0.25 else
             "Orta-düşük" if p < 0.5 else
             "Orta-yüksek" if p < 0.75 else "Yüksek")
    aciklama = (f"Olasılık = %{pct} ({yorum})\n\n"
                f"- Calreticulin: {crt_ug_ml:.3f} µg/mL\n"
                f"- ASÖ-10: {aso10}\n"
                f"- Cinsiyet: {cinsiyet}\n"
                f"- AI hastalık: {ai_hastalik}\n"
                f"- Anti-TPO: {antitpo}")
    return f"%{pct} — {yorum}", aciklama

with gr.Blocks(title="AA Risk Hesaplayıcı") as demo:
    gr.Markdown("## AA Hastalık Olasılığı Hesaplayıcı (Lojistik Regresyon Modeli)")
    with gr.Row():
        with gr.Column():
            crt_value = gr.Number(label="Calreticulin değeri", value=500, precision=3)
            crt_unit = gr.Radio(["ng/mL", "µg/mL"], value="ng/mL", label="Birim")
            aso10 = gr.Number(label="ASÖ-10 Skoru", value=10)
            cinsiyet = gr.Radio(["K", "E"], value="K", label="Cinsiyet (K/E)")
            ai_hastalik = gr.Radio(["Var", "Yok"], value="Yok", label="AI Hastalık (Var/Yok)")
            antitpo = gr.Radio(["Normal", "Yüksek"], value="Normal", label="Anti-TPO (Normal/Yüksek)")
            btn = gr.Button("Hesapla")
        with gr.Column():
            sonuc = gr.Textbox(label="Tahmin Edilen Olasılık", interactive=False)
            detay = gr.Textbox(label="Detaylar", lines=10, interactive=False)
    btn.click(predict_probability,
              inputs=[crt_value, crt_unit, aso10, cinsiyet, ai_hastalik, antitpo],
              outputs=[sonuc, detay])

if __name__ == "__main__":
    demo.launch()
