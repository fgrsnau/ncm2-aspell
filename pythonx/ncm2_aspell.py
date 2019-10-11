# -*- coding: utf-8 -*-

import subprocess

import vim
from ncm2 import Ncm2Source, getLogger


logger = getLogger(__name__)


def binary_search(collection, word):
    min = 0
    max = len(collection) - 1
    while min <= max:
        mid = (min + max) // 2
        if collection[mid].lower() < word.lower():
            min = mid + 1
        else:
            max = mid - 1
    return min


class Source(Ncm2Source):

    def __init__(self, ctx):
        super().__init__(ctx)
        self.spelllang = None
        self.dictionary = []

    def on_warmup(self, ctx):
        self.update_dictionary()

    def on_complete(self, ctx):
        self.update_dictionary()

        base = ctx['base']
        matcher = self.matcher_get(ctx['matcher'])
        matches = []
        idx = binary_search(self.dictionary, base)
        if idx < 0 or idx >= len(self.dictionary):
            return
        for word in self.dictionary[idx:idx+100]:
            item = self.match_formalize(ctx, word)
            if matcher(base, item):
                matches.append(item)
        self.complete(ctx, ctx['startccol'], matches, True)

    def update_dictionary(self):
        spell = self.nvim.eval('&spell')
        if spell:
            spelllang = self.nvim.eval('&spelllang')
        else:
            spelllang = None

        if self.spelllang != spelllang:
            self.spelllang = spelllang
            if spelllang is None:
                self.dictionary = []
            else:
                shell_command = 'aspell -d {lang} dump master | aspell -l {lang} expand'.format(lang=spelllang)
                p = subprocess.run(shell_command, shell=True, capture_output=True)
                self.dictionary = p.stdout.decode('utf8').split()
                self.dictionary = sorted(self.dictionary, key=lambda x: x.lower())


source = Source(vim)

on_warmup = source.on_warmup
on_complete = source.on_complete
