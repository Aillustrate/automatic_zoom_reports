import aspose.pdf as pdf

# Load the license
license = pdf.License()
license.set_license("License.lic")

options = pdf.TeXLoadOptions()
path = "/Users/a.marshalova/Documents/PythonProjects/ITMO_AITH_master_thesis_template/main.tex"
doc = pdf.Document(path, options)
doc.save("vkr.docx",pdf.SaveFormat.DOC_X)