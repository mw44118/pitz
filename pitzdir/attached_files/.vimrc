"This is a homemade file that probably needs to be organized better.
" vim: set filetype=vim:

" Read the first 5 lines for modelines.
:set modeline
:set modelines=5

" Set searching to be case-insensitive.
:set ignorecase

" Specify locations for tags file.
" :set tags=./tags,./TAGS,tags,TAGS,/disk2/ag/common/tags
set tags+=$HOME/.vim/tags/python.ctags,/home/matt/projects/staffknex/bazman/tags

"turn on syntax highlighting.
:syntax enable

"turn on mouse support.
":set mouse=a

"highlight matching parentheses.
set showmatch

":set indentexpr=''
:set ts=4
:set sw=4
:set expandtab
:set smartindent

" Tell vim about the terminal background color.
" :set background=light
:set background=dark

"misc overwrites of default color highlighting.
:hi Comment ctermfg=White guifg=White
:hi String ctermfg=Green guifg=Green
:hi Search cterm=bold ctermfg=6 ctermbg=4

" Set the bottom status bar to display always and customize the
" output.
:set ruler
:set laststatus=2

" This function adds the ability to figure out the indentation level for every line.
fu ShowTab()
   let TabLevel = (indent('.') / &ts )
   if TabLevel == 0
      let TabLevel='*'
   endif
   return TabLevel
endf

" This specifies what appears in the status bar at the bottom of the page.
:set statusline=%<%F\ %h%m%r%=%-14.(%l,%c%V%)\t%{ShowTab()}\ %P

"turn on hlsearch.
:set hlsearch

"a few of my mappings.
:map Q {gq}
:map <F2> :w<CR>
:map [12~ :w<CR>
:map! <F2> <ESC>:w<CR>a
:map! [12~ <ESC>:w<CR>a

" F3 does rot-13.
":map <F3> ggVGg?<CR>
":map [13~ ggVGg?<CR>
":map! <F3> <ESC>ggVGg?<CR>
":map! [13~ ggVGg?<CR>

" F3 toggles hlsearch.
:map <F3> :set invhlsearch<CR>
:map [13~ :set invhlsearch<CR>
:map! <F3> <ESC>:set invhlsearch<CR>
:map! [13~ :set invhlsearch<CR>

:map <F4> <C-w><C-w>
:map [14~ <C-w><C-w>
:map! <F4> <ESC><C-w><C-w>
:map! [14~ <ESC><C-w><C-w>

:map <F5> :bd<CR>
:map [15~ :bd<CR>
:map! <F5> <ESC>:q<CR>
:map! [15~ <ESC>:q<CR>

:map <F6> :set invwrap<CR>
:map [17~ :set invwrap<CR>
:map! <F6> <ESC>:set invwrap<CR>
:map! [17~ <ESC>:set invwrap<CR>

" F7 adds the buffer to our tags file, but you have to ENTER to confirm.
:map <F7> :! ctags -f /disk2/ag/common/tags --append %

" F8 jumps to the previous buffer.
:map <F8> :bp<CR>
:map [19~ :bp<CR>
:map! <F8> <ESC>:bp<CR>
:map! [19~ <ESC>:bp<CR>

" F9 jumps to the next buffer. Commented out since I'm tweaking F9 for
" devguy to source in this file.
":map <F9> :bn<CR>
":map [20~ :bn<CR>
":map! <F9> <ESC>:bn<CR>
":map! [20~ <ESC>:bn<CR>

" Map F10 to make.
" :map <F10> :make<CR>
" :map [21~ :make<CR>
" :map! <F10> :make<CR>
" :map! [21~ :make<CR>

"turn off indenting for html files.
autocmd BufNewFile,BufRead *.html setlocal indentexpr=''

"allow vim to set title.
:set title

"put backup files into ~/.backups, rather than .
:set backupdir=~/.backups,.

"allow me to backspace to the prev line and other stuff.
:set backspace=2

"Folding is neat.
:set foldmethod=indent
:set foldlevel=99

"vimspell...
" let spell_executable = "aspell"
" SpellSetSpellChecker aspell
" SpellSetLanguage english

"Make sure Makefile turns off expandtab
autocmd BufNewFile,BufRead *akefile set noexpandtab

"vim thinks SAS .lst files are assembly files.
autocmd BufNewFile,BufRead *.lst setlocal syntax=off
autocmd BufNewFile,BufRead *.log setlocal syntax=sas

"make vim interpret kid template files as HTML.
autocmd BufNewFile,BufRead *.kid setlocal syntax=html

" Turn on filetype plugins.
:filetype plugin on

" Indicate how to handle .pd files.
autocmd BufNewFile,BufRead *.pd setlocal filetype=html
" autocmd BufNewFile,BufRead *.pd syn region pydriver start="--startfold--" end="--endfold--" fold
" autocmd BufNewFile,BufRead *.pd syn sync fromstart
" autocmd BufNewFile,BufRead *.pd setlocal foldmethod=syntax

" This was an AG-only hack.
" map <F11> :e %<.py<CR>

" F9 Runs pychecker on the buffer.
" map <F9> :! pychecker %<CR>

" F10 executes the python program.
" map <F10> :! python %<CR>

autocmd BufNewFile,BufRead *.as setlocal filetype=javascript

" Start with an html skeleton document when opening a new *.html file.
au BufNewFile *.html execute "normal :set ai!\<CR>i<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0 Transitional//EN\">\<CR>\<CR><html>\<CR>\<CR><head>\<CR>\<CR><title></title>\<CR>\<CR></head>\<CR>\<CR><body>\<CR>\<CR><h1></h1>\<CR>\<CR></body>\<CR>\<CR></html>\<ESC>:set ai\<CR>gg"

" Make skeleton .py file.
" TODO: figure out how to use proper skeleton files.
au BufNewFile *.py execute "normal i# vim: set expandtab ts=4 sw=4 filetype=python:\<CR>\<CR>\<ESC>"

"Wrap text after 72 characters.
" au BufNewFile,BufRead *.txt setlocal textwidth=72
set textwidth=72

" This is stuff I lifted from this site: http://blog.sontek.net/2008/05/11/python-with-a-modular-ide-vim/
python << EOF
import os
import sys
import vim
for p in sys.path:
    if os.path.isdir(p):
        vim.command(r"set path+=%s" % (p.replace(" ", r"\ ")))
EOF

autocmd FileType python set omnifunc=pythoncomplete#Complete

inoremap <Nul> <C-x><C-o>

" Enable :make to list syntax errors for python.
autocmd BufRead *.py set makeprg=python\ -c\ \"import\ py_compile,sys;\ sys.stderr=sys.stdout;\ py_compile.compile(r'%')\"
autocmd BufRead *.py set efm=%C\ %.%#,%A\ \ File\ \"%f\"\\,\ line\ %l%.%#,%Z%[%^\ ]%\\@=%m

python << EOL
import vim
def EvaluateCurrentRange():
    eval(compile('\n'.join(vim.current.range),'','exec'),globals())
EOL
map <C-h> :py EvaluateCurrentRange()
