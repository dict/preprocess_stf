from IPython.display import display
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
sns.set()


def display_desc(sr):
    display(pd.DataFrame(sr.describe()))
    ax = plt.hist(sr, bins=70)
    plt.show()
    ax = plt.hist(sr, bins=70, cumulative=True)
    plt.show() 