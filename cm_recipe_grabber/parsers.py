from ingredient_parser import parse_ingredient as parse_ingredient_nlp # NLP
import ingredient_slicer

def use_ingredient_parser(ingredient):
    results = parse_ingredient_nlp(ingredient)

def use_ingredient_slicer(ingredient):
    results = ingredient_slicer.IngredientSlicer(ingredient)