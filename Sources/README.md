# 🎮 Sokoban Solver

Giải bài toán Sokoban bằng 2 thuật toán: **A*** và **DFS**

## 🚀 Cách chạy nhanh:

### **1. Game GUI (Cần pygame):**
```bash
# Cài đặt pygame trước
pip install pygame numpy

# Chạy game
python main.py
```

## 📊 Kết quả so sánh:

| Map | Thuật toán | Số bước | Thời gian | RAM |
|-----|------------|---------|-----------|---------|
| Testcases/1.txt | A* | 96 | 0.21s | 61.74 |
| Testcases/1.txt | DFS | 82 | 0.1s | 62.36 |
| Testcases/2.txt | A* | 119 | 2.17s | 68.58 |
| Testcases/2.txt | DFS | 143 | 0.81s | 68.63 |

## 📁 Cấu trúc file:

```
Sources/
├── main.py            # Game GUI
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
