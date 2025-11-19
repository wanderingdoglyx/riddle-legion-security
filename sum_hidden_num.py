
def sum_hidden_numbers(filename):
    total = 0
    with open(filename, 'r') as f:
        for line in f:
            # Skip the header or empty lines
            if line.strip() == "" or line.startswith("URL"):
                continue
            # Split by tab or whitespace
            parts = line.strip().split()
            # The last column should be the number
            try:
                num = int(parts[-1])
                total += num
            except ValueError:
                pass  # skip if it’s not a number
    return total

if __name__ == "__main__":
    filename = "./other/results.txt"  # replace with your filename
    result = sum_hidden_numbers(filename)
    print(f"Sum of HiddenNumber: {result}")