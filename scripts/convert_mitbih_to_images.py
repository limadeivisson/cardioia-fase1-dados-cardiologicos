#!/usr/bin/env python3
"""
Converte sinais do MIT-BIH Arrhythmia Database (PhysioNet/WFDB) em imagens PNG de ECG.

Pré-requisitos:
    pip install wfdb matplotlib numpy

Exemplo de uso:
    python scripts/convert_mitbih_to_images.py \
        --input_dir "/caminho/mit-bih-arrhythmia-database-1.0.0" \
        --output_dir "assets/ecg_images" \
        --limit 100
"""
import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
import wfdb

def find_record_names(input_dir: str):
    records = []
    for fname in os.listdir(input_dir):
        if fname.endswith('.hea'):
            records.append(os.path.splitext(fname)[0])
    return sorted(set(records))

def save_windows_as_images(record_path: str, output_dir: str, record_name: str,
                           segment_size: int = 1500, step: int = 750,
                           limit_remaining: int = 999999, dpi: int = 120):
    record = wfdb.rdrecord(record_path)
    signal = record.p_signal
    if signal is None or signal.shape[0] == 0:
        return 0

    lead = signal[:, 0]
    count = 0
    finite = np.isfinite(lead)
    if finite.any():
        mu = np.nanmean(lead[finite])
        sigma = np.nanstd(lead[finite]) or 1.0
        lead = (lead - mu) / sigma

    total = len(lead)
    for start in range(0, max(total - segment_size + 1, 1), step):
        if count >= limit_remaining:
            break
        end = min(start + segment_size, total)
        segment = lead[start:end]

        plt.figure(figsize=(10, 3))
        plt.plot(segment, linewidth=1.0)
        plt.title(f"MIT-BIH ECG | Record {record_name} | Samples {start}-{end}")
        plt.xlabel("Amostras")
        plt.ylabel("Amplitude normalizada")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        out_name = f"{record_name}_{start:06d}_{end:06d}.png"
        out_path = os.path.join(output_dir, out_name)
        plt.savefig(out_path, dpi=dpi)
        plt.close()
        count += 1

    return count

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', required=True, help='Pasta com arquivos MIT-BIH (.dat/.hea)')
    parser.add_argument('--output_dir', default='assets/ecg_images', help='Pasta de saída das imagens')
    parser.add_argument('--limit', type=int, default=100, help='Número máximo de imagens a gerar')
    parser.add_argument('--segment_size', type=int, default=1500, help='Tamanho da janela do ECG')
    parser.add_argument('--step', type=int, default=750, help='Passo entre janelas')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    records = find_record_names(args.input_dir)
    if not records:
        raise FileNotFoundError("Nenhum arquivo .hea foi encontrado na pasta informada.")

    total_saved = 0
    for rec in records:
        if total_saved >= args.limit:
            break
        rec_path = os.path.join(args.input_dir, rec)
        remaining = args.limit - total_saved
        saved = save_windows_as_images(
            record_path=rec_path,
            output_dir=args.output_dir,
            record_name=rec,
            segment_size=args.segment_size,
            step=args.step,
            limit_remaining=remaining
        )
        total_saved += saved
        print(f"[OK] Registro {rec}: {saved} imagens geradas | Total: {total_saved}")

    print(f"\nConcluído. Total de imagens geradas: {total_saved}")
    print(f"Saída: {os.path.abspath(args.output_dir)}")

if __name__ == '__main__':
    main()
