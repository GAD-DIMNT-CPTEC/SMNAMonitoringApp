#! /usr/bin/env python3

import panel as pn

def show_modal():
    modal_btn = pn.widgets.Button(name='📖 Informações Gerais', button_type='primary')
    text_info1 = pn.Column("TESTE")
    
    modal_btn.on_click(show_modal_1)

    return pn.Column(modal_btn)

#def show_modal_1(event):
#    app.modal[0].clear()
#    app.modal[0].append(text_info1)
#    app.open_modal()
    
