# coding: utf-8

file_orig_paths = [
    "billy_ikea", "billy_nitori", "billy_muji",
    "erik_ikea", "erik_nitori", "erik_muji",
    "malm_ikea", "malm_nitori", "malm_muji",
    "kullen_ikea", "kullen_nitori", "kullen_muji",
    "millberget_ikea", "millberget_nitori", "millberget_muji"
]

# 空のファイルを作っていく
for i, file_orig_path in enumerate(file_orig_paths):
    for i in range(3):
        file_path = "./ja/" + file_orig_path + "{}.txt".format(i + 1)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("あい") # "あ"だけだとファイル出力が変になる（原因不明）