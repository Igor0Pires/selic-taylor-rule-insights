# Plots
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path

# plt.style.use('../data/plots/plot_style.mplstyle')

class Plotter:
    def __init__(self, data):
        self.data = data
    
    def plot_inflation(self, load_data: bool):
        """Plot inflation rate against target and expected inflation.
        
        when use: visualize inflation data eda
        """

        self.data['Date'] = self.data['Date'].dt.to_timestamp()

        fig = plt.figure(figsize=(12, 6), facecolor="#FAFAF8")

        fig.add_artist(plt.Line2D([0.05, 0.95], [0.96, 0.96], color= "#44FF00", lw=3, transform=fig.transFigure)) #----

        ax = plt.gca()
        ax.set_facecolor("#FAFAF8")
        
        plt.plot(self.data['Date'], self.data['inflation_12m'], label='12-Month Inflation Rate', color='blue')

        plt.plot(self.data.dropna(subset=['upper_limit'])['Date'], self.data.dropna(subset=['upper_limit'])['inflation_target'], label='Inflation Target', color='orange')

        plt.plot(self.data['Date'], self.data['focus_expected_inflation'], label='Expected Inflation', color='green', linestyle='--')
        
        plt.plot(self.data.dropna(subset=['upper_limit'])['Date'], self.data.dropna(subset=['upper_limit'])['lower_limit'], label='Lower Limit', color='red', linestyle=':')
        plt.plot(self.data.dropna(subset=['upper_limit'])['Date'], self.data.dropna(subset=['upper_limit'])['upper_limit'], label='Upper Limit', color='red', linestyle=':')

        plt.title('Inflation Rate vs Target')
        plt.xlabel('Date')
        plt.ylabel('Inflation Rate (%)')
        plt.legend()
        
        # Remover spines (bordas)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        
        # Apenas grid horizontal, sutil
        ax.grid(True, axis='y', color="#D9D9D9", linestyle="-", linewidth=0.5, zorder=0, alpha=0.6)

        if load_data:
            plt.savefig('./data/plots/inflation_vs_target.png')

    def plot_selic(self, load_data: bool):
        """Plot SELIC rate against Taylor Rule suggested rate.
        
        when use: visualize selic data eda
        """

        fig = plt.figure(figsize=(12, 6), facecolor="#FAFAF8")

        fig.add_artist(plt.Line2D([0.05, 0.95], [0.96, 0.96], color= "#44FF00", lw=3, transform=fig.transFigure)) #----

        ax = plt.gca()
        ax.set_facecolor("#FAFAF8")
        
        plt.plot(self.data['Date'], self.data['selic_target'], label='SELIC Rate', color='blue')

        plt.title('SELIC Rate vs Taylor Rule Suggested Rate')
        plt.xlabel('Date')
        plt.ylabel('Interest Rate (%)')
        plt.legend()
        
        # Remover spines (bordas)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        
        # Apenas grid horizontal, sutil
        ax.grid(True, axis='y', color="#D9D9D9", linestyle="-", linewidth=0.5, zorder=0, alpha=0.6)

        if load_data:
            plt.savefig('./data/plots/selic_vs_taylor.png')
        

    def plot_output_and_exchange(self, load_data: bool):
        """Plot output gap and exchange rate over time.
        
        when use: visualize output gap and exchange rate data eda
        """

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 6), facecolor="#FAFAF8")

        fig.add_artist(plt.Line2D([0.05, 0.95], [0.96, 0.96], color="#44FF00", lw=3, transform=fig.transFigure))

        # Plot 1: Output Gap and Output
        ax1.set_facecolor("#FAFAF8")
        color = 'tab:blue'
        ax1.set_ylabel('Output Gap (%)', color=color)
        ax1.plot(self.data['Date'], self.data['output_gap'], color=color, label='Output Gap')
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.set_title('Output Gap and Output')
        

        # Plot 2: Exchange Rate Var and Exchange Rate
        ax2.set_facecolor("#FAFAF8")
        color = 'tab:orange'
        ax2.set_ylabel('Exchange Rate Variation (%)', color=color)
        ax2.plot(self.data['Date'], self.data['exchange_rate_var'], color=color, label='Exchange Rate Variation')
        ax2.tick_params(axis='y', labelcolor=color)
        ax2.set_title('Exchange Rate Variation and Exchange Rate')


        # Remove spines
        for ax in [ax1, ax2]:
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)
        
        # Grid
        ax1.grid(True, axis='y', color="#D9D9D9", linestyle="-", linewidth=0.5, zorder=0, alpha=0.6)
        ax2.grid(True, axis='y', color="#D9D9D9", linestyle="-", linewidth=0.5, zorder=0, alpha=0.6)

        plt.suptitle('Output Gap and Exchange Rate Over Time')
        plt.tight_layout()

        if load_data:
            plt.savefig('./data/plots/output_gap_and_exchange_rate.png')
        plt.show()