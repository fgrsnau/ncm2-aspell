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

    def on_warmup(self, ctx):
        bufnr = ctx['bufnr']
        logger.info('on_warmup for buffer %s', bufnr)

        spell = self.nvim.eval('&spell')
        spelllang = self.nvim.eval('&spelllang')
        logger.info('spell=%s spelllang=%s', spell, spelllang)

        self.dictionary = []
        if spell:
            shell_command = 'aspell -d {lang} dump master | aspell -l {lang} expand'.format(lang=spelllang)
            p = subprocess.run(shell_command, shell=True, capture_output=True)
            self.dictionary = p.stdout.decode('utf8').split('\n')
            self.dictionary = sorted(self.dictionary, key=lambda x: x.lower())
        logger.info('dictionary size = %s', len(self.dictionary))

    def on_complete(self, ctx):
        base = ctx['base']
        logger.debug('on_complete -> base=%s', base)
        matcher = self.matcher_get(ctx['matcher'])
        matches = []
        idx = binary_search(self.dictionary, base)
        if idx < 0 or idx >= len(self.dictionary):
            return
        logger.debug('base=%s idx=%s word=%s', base, idx, self.dictionary[idx])
        for word in self.dictionary[idx:idx+100]:
            item = self.match_formalize(ctx, word)
            if matcher(base, item):
                matches.append(item)
        self.complete(ctx, ctx['startccol'], matches, True)


source = Source(vim)

on_warmup = source.on_warmup
on_complete = source.on_complete
