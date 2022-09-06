import matplotlib.pyplot as plt

if __name__ == "__main__":
    fig = plt.figure()
    #ax = fig.add_axes([0, 0, 1, 1])
    years = [y for y in range(1988, 2021)]
    #papers = [1015, 1190, 1279, 1429, 1599, 1888, 2163, 2780, 4177, 5341, 7638, 9215, 10958, 13037, 16771, 20739, 28107,
    #          32107, 37253, 44537, 55430, 63349, 74815, 93714, 116394, 137157, 144997, 128587, 141907, 146259, 131861,
    #          72500, 3242]
    # unfiltered all domains

    # only unique cs domain
    # old numbers
    #papers = [56,77,96,95,168,220,323,411,457,670,994,1157,1566,1881,2909,4110,5774,7615,8719,9976,11179,12557,14032,15156,17593,19222,19339,19713,20977,22160,23119,15549,1082]

    # with self citations removed
    papers = [29,46,66,55,108,148,230,287,291,444,691,806,1059,1228,2042,2869,3987,5316,5869,6333,6835,7351,8131,8283,9659,10475,9798,10152,10322,10094,10173,6291,394]
    print(f"Sum over all years {sum(papers)}")
    train_years = years[:-3]
    train_papers = papers[:-3]

    val_years = years[-3:-2]
    val_papers = papers[-3:-2]

    test_years = years[-2:]
    test_papers = papers[-2:]

    plt.bar(train_years, train_papers)
    plt.bar(val_years,val_papers)
    plt.bar(test_years, test_papers)

    plt.ylabel('Number of Papers')
    plt.xlabel('Published Year')
    plt.title('Papers per year in filtered S2ORC dataset')
    plt.legend(labels=['Train split','Validation split','Test split'])
    #plt.show()
    plt.savefig('s2orc-year-distribution.png')
