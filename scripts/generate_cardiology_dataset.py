#!/usr/bin/env python3
"""
Gera um dataset cardiológico sintético/profissional com 300+ linhas em CSV/XLSX.

Pré-requisitos:
    pip install pandas openpyxl numpy

Exemplo:
    python scripts/generate_cardiology_dataset.py --rows 300 --output_dir datasets
"""
import os
import argparse
import numpy as np
import pandas as pd

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def generate_dataset(n=300, seed=42):
    rng = np.random.default_rng(seed)

    idade = rng.integers(29, 86, n)
    sexo = rng.choice(['Masculino', 'Feminino'], size=n, p=[0.56, 0.44])
    pressao_sistolica = np.clip(rng.normal(132, 18, n).round(), 90, 210).astype(int)
    pressao_diastolica = np.clip(rng.normal(82, 12, n).round(), 55, 130).astype(int)
    colesterol = np.clip(rng.normal(222, 42, n).round(), 120, 420).astype(int)
    glicemia = np.clip(rng.normal(108, 28, n).round(), 65, 280).astype(int)
    freq_cardiaca_repouso = np.clip(rng.normal(76, 13, n).round(), 45, 130).astype(int)
    saturacao_o2 = np.clip(rng.normal(97, 2, n).round(), 85, 100).astype(int)
    imc = np.clip(rng.normal(28.4, 4.9, n), 17.5, 45.0).round(1)
    tabagismo = rng.choice(['Nunca', 'Ex-fumante', 'Atual'], size=n, p=[0.48, 0.27, 0.25])
    diabetes = rng.choice(['Não', 'Sim'], size=n, p=[0.74, 0.26])
    hipertensao = np.where(pressao_sistolica >= 140, 'Sim', rng.choice(['Não', 'Sim'], size=n, p=[0.75, 0.25]))
    historico_familiar = rng.choice(['Não', 'Sim'], size=n, p=[0.55, 0.45])
    atividade_fisica = rng.choice(['Baixa', 'Moderada', 'Alta'], size=n, p=[0.37, 0.45, 0.18])
    dor_toracica = rng.choice(['Ausente', 'Atípica', 'Típica'], size=n, p=[0.46, 0.32, 0.22])
    falta_de_ar = rng.choice(['Não', 'Sim'], size=n, p=[0.66, 0.34])
    palpitacoes = rng.choice(['Não', 'Sim'], size=n, p=[0.71, 0.29])
    ecg_resultado = rng.choice(['Normal', 'Alteração ST-T', 'Hipertrofia VE', 'Arritmia'], size=n, p=[0.48, 0.18, 0.16, 0.18])

    sexo_m = (sexo == 'Masculino').astype(int)
    fumante_atual = (tabagismo == 'Atual').astype(int)
    diabetes_sim = (diabetes == 'Sim').astype(int)
    hist_sim = (historico_familiar == 'Sim').astype(int)
    dor_tipica = (dor_toracica == 'Típica').astype(int)
    falta_ar_sim = (falta_de_ar == 'Sim').astype(int)
    palp_sim = (palpitacoes == 'Sim').astype(int)
    ecg_anormal = (ecg_resultado != 'Normal').astype(int)
    atividade_baixa = (atividade_fisica == 'Baixa').astype(int)

    linear = (-8.5 + 0.045 * idade + 0.018 * (pressao_sistolica - 120) + 0.010 * (colesterol - 180)
              + 0.012 * (glicemia - 95) + 0.11 * (imc - 25) + 0.55 * sexo_m + 0.95 * fumante_atual
              + 0.85 * diabetes_sim + 0.70 * hist_sim + 1.10 * dor_tipica + 0.72 * falta_ar_sim
              + 0.50 * palp_sim + 0.95 * ecg_anormal + 0.58 * atividade_baixa)
    prob = sigmoid(linear)
    risco_binario = rng.binomial(1, np.clip(prob, 0.03, 0.97))
    risco_clinico = np.where(prob < 0.22, 'Baixo', np.where(prob < 0.48, 'Moderado', 'Alto'))

    sintomas_principais = []
    for i in range(n):
        sintomas = []
        if dor_toracica[i] != 'Ausente':
            sintomas.append('dor torácica')
        if falta_de_ar[i] == 'Sim':
            sintomas.append('dispneia')
        if palpitacoes[i] == 'Sim':
            sintomas.append('palpitações')
        if not sintomas:
            sintomas.append('assintomático')
        sintomas_principais.append(', '.join(sintomas))

    return pd.DataFrame({
        'idade': idade,
        'sexo': sexo,
        'pressao_sistolica_mmHg': pressao_sistolica,
        'pressao_diastolica_mmHg': pressao_diastolica,
        'colesterol_mg_dL': colesterol,
        'glicemia_mg_dL': glicemia,
        'freq_cardiaca_repouso_bpm': freq_cardiaca_repouso,
        'saturacao_o2_percent': saturacao_o2,
        'imc': imc,
        'tabagismo': tabagismo,
        'diabetes': diabetes,
        'hipertensao': hipertensao,
        'historico_familiar_cardiaco': historico_familiar,
        'atividade_fisica': atividade_fisica,
        'dor_toracica': dor_toracica,
        'falta_de_ar': falta_de_ar,
        'palpitacoes': palpitacoes,
        'sintomas_principais': sintomas_principais,
        'resultado_ecg': ecg_resultado,
        'probabilidade_risco_cardiaco': prob.round(4),
        'classe_risco_cardiaco': risco_clinico,
        'evento_cardiaco_alvo': risco_binario
    })

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--rows', type=int, default=300)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--output_dir', default='datasets')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    df = generate_dataset(n=args.rows, seed=args.seed)

    csv_path = os.path.join(args.output_dir, f'pacientes_cardiacos_{args.rows}.csv')
    xlsx_path = os.path.join(args.output_dir, f'pacientes_cardiacos_{args.rows}.xlsx')

    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    df.to_excel(xlsx_path, index=False)

    print(f'[OK] CSV salvo em:  {os.path.abspath(csv_path)}')
    print(f'[OK] XLSX salvo em: {os.path.abspath(xlsx_path)}')
    print(df.head())

if __name__ == '__main__':
    main()
