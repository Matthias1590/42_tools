#!/bin/bash

git clone https://github.com/Matthias1590/42_tools.git ~/42_tools

echo "source ~/42_tools/.zshrc" >> ~/.zshrc
echo "source ~/42_tools/.bashrc" >> ~/.bashrc
echo "source ~/42_tools/.profile" >> ~/.profile
echo "source ~/42_tools/.vimrc" >> ~/.vimrc

source ~/.zshrc

echo "42 tools installed, run '42 --help' to see available commands"
