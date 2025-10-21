# 🎮 Sokoban Solver

Giải bài toán Sokoban bằng 2 thuật toán: **A*** và **DFS**

## 🚀 Cách chạy nhanh:

### **1. Chạy thuật toán riêng lẻ (Khuyến nghị):**
```bash
# A* Algorithm
python run_astar.py --input input/1.txt --output result_astar.txt

# DFS Algorithm  
python run_dfs.py --input input/1.txt --output result_dfs.txt
```

### **2. Demo so sánh cả 2 thuật toán:**
```bash
python demo.py
```

### **3. Game GUI (Cần pygame):**
```bash
# Cài đặt pygame trước
pip install pygame numpy

# Chạy game
python main.py
```

## 📊 Kết quả so sánh:

| Map | Thuật toán | Số bước | Thời gian | Ưu điểm |
|-----|------------|---------|-----------|---------|
| input/1.txt | A* | 69 | 0.15s | Đường ngắn nhất |
| input/1.txt | DFS | 83 | 0.04s | Nhanh hơn |
| input/2.txt | A* | 33 | 0.07s | Tối ưu |
| input/2.txt | DFS | 58 | 0.09s | Đơn giản |

## 📁 Cấu trúc file:

```
sokoban/
├── input/              # Maps đầu vào
├── run_astar.py        # Chạy A* với file
├── run_dfs.py         # Chạy DFS với file  
├── main.py            # Game GUI
├── demo.py            # Demo so sánh
├── astar.py           # Module A*
├── dfs.py             # Module DFS
└── sokoban_helpers.py # Helper functions
```

## 🎯 Kết quả:

- **Solution**: Chuỗi di chuyển (u=up, d=down, l=left, r=right, UPPERCASE=push)
- **Runtime**: Thời gian chạy
- **States explored**: Số trạng thái khám phá

## 🔧 Troubleshooting:

### **Lỗi "No module named 'pygame'":**
```bash
pip install pygame numpy
```

### **Lỗi encoding:**
- Đã sửa trong code, không cần lo lắng

## 📈 Kết luận:

- **A***: Tìm đường ngắn nhất, tốt cho bài toán phức tạp
- **DFS**: Nhanh, ít bộ nhớ, tốt cho bài toán đơn giản
- **Khuyến nghị**: Dùng A* cho kết quả tối ưu, DFS cho tốc độ
