import trajectory as tra

def main():
    sample = tra.validate_sample(0.0, [0.1, -0.2])
    print(sample)

if __name__ == "__main__":
    main()