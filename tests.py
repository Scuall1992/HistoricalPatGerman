with open('test.txt', 'r', encoding='utf-8') as f:
    with open('test1.txt', 'r', encoding='utf-8') as g:
        f_lines = f.read().split("\n")
        g_lines = g.read().split("\n")
        count = 0
        for i in range(len(f_lines)):
            if f_lines[i].lower() != g_lines[i].lower():
                print(i + 1, f_lines[i], g_lines[i])
                count += 1
        print(count)
