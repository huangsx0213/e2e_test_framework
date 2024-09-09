fill_by_js_script = '''
    function setNativeValue(element,value) {{
        const {{
            set: valueSetter
        }} = Object.getOwnPropertyDescriptor(element,'value') || {{}};
        const prototype = Object.getPrototypeOf(element);
        const {{
            set: prototypeValueSetter
        }} = Object.getOwnPropertyDescriptor(prototype,'value') || {{}};

        if (prototypeValueSetter && valueSetter !== prototypeValueSetter) {{
            prototypeValueSetter.call(element,value);
        }}

        else if (valueSetter) {{
            valueSetter.call(element,value);
        }} else {{
            throw new Error('The given element does not have a value setter');
        }}
    }}
    function fireEvent(element,value) {{
    setNativeValue(element,value);
    element.dispatchEvent(new Event('change',{{bubbles: true}}));
    }}
    fireEvent(arguments[0], '{text}')
'''

click_by_js_script = '''
    function clickByJsFireEvent(element) {
        // Check if the element is not null and is an instance of HTMLElement
        if (element instanceof HTMLElement) {
            element.click(); // Programmatically click the element
            element.dispatchEvent(new Event('click', { bubbles: true })); // Dispatch the click event, making it bubble up
        } else {
            throw new Error('The given element is not a valid HTML element');
        }
    }
    clickByJsFireEvent(arguments[0]);
'''
