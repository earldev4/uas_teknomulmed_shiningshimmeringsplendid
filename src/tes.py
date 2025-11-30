import pandas as pd
from rich import print as rprint

def main():
    # 1. Tes library 'rich' (output berwarna)
    rprint("[bold green]===== TES PROYEK BERHASIL =====")
    rprint("Library [cyan]rich[/cyan] berhasil di-load dan dijalankan.")

    # 2. Tes library 'pandas' (membuat DataFrame)
    data = {
        'Nama': ['Andi', 'Budi', 'Citra'],
        'Status': ['Hadir', 'Hadir', 'Hadir']
    }
    df = pd.DataFrame(data)
    
    rprint("\nLibrary [yellow]pandas[/yellow] juga berhasil di-load.")
    rprint("Data berhasil dibuat:")
    
    # Mencetak DataFrame (rich akan membuatnya cantik)
    rprint(df)
    rprint("[bold green]===============================[/bold green]")

if __name__ == "__main__":
    main()