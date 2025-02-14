import unittest
import pint

test_data = [
    {
        "input": "1 cup red or yellow pepper",
        "output": {
            "name": "red or yellow pepper",
            "unit": "cup",
            "amount": 1,
        }
    },
    {
        "input": "2 t baking powder",
        "output": {
            "name": "baking powder",
            "unit": "teaspoon",
            "amount": 2
        }    
    },
    {
        "input": "2 t. baking powder",
        "output": {
            "name": "baking powder",
            "unit": "teaspoon",
            "amount": 2
        }    
    },
    {
        "input": "2 T baking powder",
        "output": {
            "name": "baking powder",
            "unit": "tablespoon",
            "amount": 2
        }    
    },
    {
        "input": "2 T. baking powder",
        "output": {
            "name": "baking powder",
            "unit": "tablespoon",
            "amount": 2
        }    
    },
        {
        "input": "2t baking powder",
        "output": {
            "name": "baking powder",
            "unit": "teaspoon",
            "amount": 2
        }    
    },
    {
        "input": "2t. baking powder",
        "output": {
            "name": "baking powder",
            "unit": "teaspoon",
            "amount": 2
        }    
    },
    {
        "input": "2T baking powder",
        "output": {
            "name": "baking powder",
            "unit": "tablespoon",
            "amount": 2
        }    
    },
    {
        "input": "2T. baking powder",
        "output": {
            "name": "baking powder",
            "unit": "tablespoon",
            "amount": 2
        }    
    },
        {
        "input": "2 t, baking powder",
        "output": {
            "name": "baking powder",
            "unit": "teaspoon",
            "amount": 2
        }    
    },
    {
        "input": "2 t., baking powder",
        "output": {
            "name": "baking powder",
            "unit": "teaspoon",
            "amount": 2
        }    
    },
    {
        "input": "2 T, baking powder",
        "output": {
            "name": "baking powder",
            "unit": "tablespoon",
            "amount": 2
        }    
    },
    {
        "input": "2 T., baking powder",
        "output": {
            "name": "baking powder",
            "unit": "tablespoon",
            "amount": 2
        }    
    },
        {
        "input": "2t, baking powder",
        "output": {
            "name": "baking powder",
            "unit": "teaspoon",
            "amount": 2
        }    
    },
    {
        "input": "2t., baking powder",
        "output": {
            "name": "baking powder",
            "unit": "teaspoon",
            "amount": 2
        }    
    },
    {
        "input": "2T,baking powder",
        "output": {
            "name": "baking powder",
            "unit": "tablespoon",
            "amount": 2
        }    
    },
    {
        "input": "2T.,baking powder",
        "output": {
            "name": "baking powder",
            "unit": "tablespoon",
            "amount": 2
        }    
    },
                {
        "input": "2 t,baking powder",
        "output": {
            "name": "baking powder",
            "unit": "teaspoon",
            "amount": 2
        }    
    },
    {
        "input": "2 t.,baking powder",
        "output": {
            "name": "baking powder",
            "unit": "teaspoon",
            "amount": 2
        }    
    },
    {
        "input": "2 T,baking powder",
        "output": {
            "name": "baking powder",
            "unit": "tablespoon",
            "amount": 2
        }    
    },
    {
        "input": "2 T.,baking powder",
        "output": {
            "name": "baking powder",
            "unit": "tablespoon",
            "amount": 2
        }    
    },
        {
        "input": "2t,baking powder",
        "output": {
            "name": "baking powder",
            "unit": "teaspoon",
            "amount": 2
        }    
    },
    {
        "input": "2t.,baking powder",
        "output": {
            "name": "baking powder",
            "unit": "teaspoon",
            "amount": 2
        }    
    },
    {
        "input": "2T,baking powder",
        "output": {
            "name": "baking powder",
            "unit": "tablespoon",
            "amount": 2
        }    
    },
    {
        "input": "2T.,baking powder",
        "output": {
            "name": "baking powder",
            "unit": "tablespoon",
            "amount": 2
        }    
    },
             ]

import re
def clean_abbreviated_spoons(ingredient):
    ptn = re.compile("([\d]+)( *[tT][\.?\,? ]+)")
    def make_repl(m):
        
        if m.group(2).strip().startswith("t"):
            return m.group(1) + " teaspoon "
        else:
            return m.group(1) + " tablespoon "
        
    return ptn.sub(make_repl, ingredient)

class IngredientParsingTest(unittest.TestCase):
    def test_parse(self):
        from ingredient_parser import parse_ingredient
        for test in test_data:
            print(f"{test}")
            out = parse_ingredient(clean_abbreviated_spoons(test["input"]))
            print(f"{out}")

            self.assertEqual(out.name.text, test["output"]["name"])
            self.assertEqual(str(out.amount[0].unit), test["output"]["unit"])
            self.assertEqual(out.amount[0].quantity, test["output"]["amount"])

if __name__ == "__main__":
    unittest.main()