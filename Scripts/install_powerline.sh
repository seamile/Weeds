#!/bin/bash
# download the powerline-font config and the Symbols font
mkdir -p $HOME/.fonts.conf.d/
cd $HOME/.fonts.conf.d/
wget https://github.com/Lokaltog/powerline/raw/develop/font/10-powerline-symbols.conf
wget https://github.com/Lokaltog/powerline/raw/develop/font/PowerlineSymbols.otf

# clone powerline-fonts
git clone https://github.com/Lokaltog/powerline-fonts.git $HOME/.fonts/powerline-fonts

# reset font cache
fc-cache -fv $HOME/.fonts

# download powerline-shell
git clone https://github.com/milkbikis/powerline-shell $HOME/.powerline-shell
cd $HOME/.powerline-shell
cp -f config.py.dist config.py
python $HOME/.powerline-shell/install.py
rm -f $HOME/.powerline-shell.py
ln -s $HOME/.powerline-shell/powerline-shell.py $HOME/.powerline-shell.py

# modify bashrc
echo '
function _update_ps1() {
   export PS1="$(~/.powerline-shell.py $? --colorize-hostname 2> /dev/null)"
}
export PROMPT_COMMAND="_update_ps1; $PROMPT_COMMAND"' >> $HOME/.bashrc
