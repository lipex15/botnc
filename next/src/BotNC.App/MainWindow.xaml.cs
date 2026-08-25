using System.Windows;
using BotNC.App.ViewModels;

namespace BotNC.App;

public partial class MainWindow : Window
{
    public MainWindow(MainWindowViewModel viewModel)
    {
        InitializeComponent();
        DataContext = viewModel;
    }
}
