from importlib import reload

FILE_NUMBERS = [1,2,3,4,5,10,20,30,40,50,60,70,80,90,100]
for FILE_NUMBER in FILE_NUMBERS:
    print(f"Iterating at {FILE_NUMBER}")
    import main # Change main to be either main or prevMain
    reload(main)