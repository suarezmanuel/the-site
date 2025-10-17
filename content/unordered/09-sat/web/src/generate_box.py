import sys
import re 

def strip_html(text):
    """Removes HTML tags from a string."""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def main(args): # assummes header is first line

    infile = args[0]
    outfile = args[1]

    col_count = 0
    row_count = 0 
    header = ""

    with open(infile, 'r') as f: # open file to box
        for line in f:
            if row_count == 0:
                header = line.strip() + ' '
            col_count = max(col_count, len(line.strip()))
            row_count += 1

    padding_horizontal = 3 
    padding_vertical = 1

    top_line = '++' + '=' * (col_count + padding_horizontal * 2) + '++\n' 
    top_line = header + top_line[len(header):]

    bottom_line = '++' + '=' * (col_count + padding_horizontal * 2) + '++\n' 

    with open(infile, 'r') as f, open(outfile, 'w') as g:

        f.readline()
        g.write(top_line)

        for _ in range(padding_vertical):
            g.write('||' + ' ' * (2*padding_horizontal + col_count) + '||\n')

        for _ in range (row_count-1):
            line = f.readline().strip()
            line_nohtml = strip_html(line)

            g.write('||' + ' ' * padding_horizontal + line.ljust(col_count+len(line)-len(line_nohtml)) + ' ' * padding_horizontal + '||\n')

        for _ in range(padding_vertical):
            g.write('||' + ' ' * (2*padding_horizontal + col_count) + '||\n')

        g.write(bottom_line)

if __name__ == "__main__":
    main(sys.argv[1:])
