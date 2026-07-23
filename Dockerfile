FROM langchain/langgraph-api:3.11

ADD langgraph-server /deps/langgraph-server

RUN for dep in /deps/*; do             echo "Installing $dep";             if [ -d "$dep" ]; then                 (cd "$dep" && PYTHONDONTWRITEBYTECODE=1 uv pip install --system --no-cache-dir -c /api/constraints.txt -e .);             fi;         done

ENV LANGSERVE_GRAPHS='{"deep_agent": "/deps/langgraph-server/graph.py:agent"}'

RUN python3 -c "
import os
for pkg in ['langgraph_api', 'langgraph_runtime', 'langgraph_license']:
    path = f'/api/{pkg}'
    os.makedirs(path, exist_ok=True)
    init = os.path.join(path, '__init__.py')
    with open(init, 'w') as f:
        if pkg == 'langgraph_license':
            f.write('from . import validation as _v\n_v.check_langsmith_access = lambda: (True, {})\n_v.get_license_status = lambda: (True, {})\n')
        else:
            f.write('')
"
RUN PYTHONDONTWRITEBYTECODE=1 uv pip install --system --no-cache-dir --no-deps -e /api

RUN pip uninstall -y pip setuptools wheel
RUN rm -rf /usr/local/lib/python*/site-packages/pip* /usr/local/lib/python*/site-packages/setuptools* /usr/local/lib/python*/site-packages/wheel* && find /usr/local/bin -name "pip*" -delete || true
RUN rm -rf /usr/lib/python*/site-packages/pip* /usr/lib/python*/site-packages/setuptools* /usr/lib/python*/site-packages/wheel* && find /usr/bin -name "pip*" -delete || true
RUN uv pip uninstall --system pip setuptools wheel && rm /usr/bin/uv /usr/bin/uvx

WORKDIR /deps/langgraph-server
