{{ fullname }}
{{ underline }}

.. py:function:: {{ obj.__name__ }}({{ signature }})

   {{ obj.__doc__ }}

   **Parameters:**
   {% for param in params %}
   - **{{ param.name }}** (*{{ param.type }}*): {{ param.description }}
   {% endfor %}

   **Returns:**
   {{ return_type }}: {{ return_description }}
