#PLOT TWO Y AXES
def y_fmt(y, pos):
    decades = [1e9, 1e6, 1e3, 1e0, 1e-3, 1e-6, 1e-9 ]
    suffix  = ["G", "M", "k", "" , "m" , "u", "n"  ]
    if y == 0:
        return str(0)
    for i, d in enumerate(decades):
        if np.abs(y) >=d:
            val = y/float(d)
            signf = len(str(val).split(".")[1])
            if signf == 0:
                return '{val:d} {suffix}'.format(val=int(val), suffix=suffix[i])
            else:
                if signf == 1:
                    if str(val).split(".")[1] == "0":
                       return '{val:d} {suffix}'.format(val=int(round(val)), suffix=suffix[i]) 
                tx = "{"+"val:.{signf}f".format(signf = signf) +"} {suffix}"
                return tx.format(val=val, suffix=suffix[i])

                #return y
    return y

plt.rcParams['figure.figsize'] = 12, 10
plt.rcParams.update({'font.size': 33, 'lines.linewidth' : 10})

fig, ax1 = plt.subplots()

ax2 = ax1.twinx()
ax1.plot(plot_df_savings_.x, plot_df_savings_.y1, '#feb24c')
ax1.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(y_fmt))
ax2.plot(plot_df_waste_.x, plot_df_waste_.y2, '#0868ac')

ax1.set_xlabel('No. SKUs')
ax1.set_ylabel('Total Savings (€)', color='#feb24c')
ax2.set_ylabel('Total Waste (metric tons)', color='#0868ac')

plt.show()