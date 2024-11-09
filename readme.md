original IGOR script function from Tom Savenije's group transcribed to a Python class 

Web Ui made with streamlit: https://www.streamlit.io/

   
The model describes a 2-layer sample stack inside a microwave cavity. The 2 sample layers are refered to as substrate and sample layer. From the modeling side, both are represented by the same model and parameters: a thickness, a dieelectric contant and a conductivity. A typical example is a thin conducting layer on a thick glass substrate. By setting one of the layers to thickness=0, the model reduces to a 1 layer model.    

run with the following command:
`streamlit run app.py`
