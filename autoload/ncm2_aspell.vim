if get(s:, 'loaded', 0)
    finish
endif
let s:loaded = 1

let g:ncm2_aspell#proc = yarp#py3({
    \ 'module': 'ncm2_aspell',
    \ 'on_load': { -> ncm2#set_ready(g:ncm2_aspell#source)}
    \ })

let g:ncm2_aspell#source = extend(get(g:, 'ncm2_aspell#source', {}), {
            \ 'name': 'aspell',
            \ 'ready': 0,
            \ 'priority': 8,
            \ 'mark': 's',
            \ 'on_complete': 'ncm2_aspell#on_complete',
            \ 'on_warmup': 'ncm2_aspell#on_warmup',
            \ }, 'keep')

func! ncm2_aspell#init()
    call ncm2#register_source(g:ncm2_aspell#source)
endfunc

func! ncm2_aspell#on_warmup(ctx)
    call g:ncm2_aspell#proc.try_notify('on_warmup', a:ctx)
endfunc

func! ncm2_aspell#on_complete(ctx)
    call g:ncm2_aspell#proc.try_notify('on_complete', a:ctx)
endfunc

func! ncm2_aspell#on_event(event)
    call g:ncm2_aspell#proc.try_notify('on_event', a:event, bufnr('%'))
endfunc

