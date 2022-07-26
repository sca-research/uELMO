# Note for developpers
Yan Yan, last updated 26/07/2022

## Coding style
A coding style is provided here. Use it with the Linux indent tool:
```shell
sudo apt install indent
cp indent.pro ~/.indent.pro
```

Please **ALWAYS** format the source code before commit:
```shell
indent {SOURCE_FILES}
git stage {SOURCE_FILES}
git commit
```

## vimrc
For vim users, you may use my vim configuration in this folder:
```shell
cp vimrc ~/.vimrc
```
