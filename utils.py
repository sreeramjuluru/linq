

def convert_list_wtforms_choices(list_to_convert):
      print list_to_convert
      choices = []
      i =1
      for item in list_to_convert:
          choices.append((item.id,item))
          i = i+1
      return choices

