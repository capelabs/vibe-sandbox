#!/bin/bash

OPENSEARCH_HOST="opensearch"
OPENSEARCH_PORT="9200"

# Wait for OpenSearch to be up
echo "Waiting for OpenSearch to be available at ${OPENSEARCH_HOST}:${OPENSEARCH_PORT}..."

until curl -s "http://${OPENSEARCH_HOST}:${OPENSEARCH_PORT}" >/dev/null; do
    sleep 2
done
echo "OpenSearch is up."

# Enable MCP option
echo "Enabling MCP option..."
RESPONSE=$(curl -s -X PUT "http://${OPENSEARCH_HOST}:${OPENSEARCH_PORT}/_cluster/settings/" \
    -H 'Content-Type: application/json' \
    -d '{"persistent":{"plugins.ml_commons.mcp_server_enabled":"true"}}')

echo "Response from OpenSearch:"
echo "${RESPONSE}"

# Check if the response indicates success
if echo "${RESPONSE}" | grep -q '"acknowledged":true'; then
    echo "MCP server enabled successfully."
else
    echo "Failed to enable MCP server. Response: ${RESPONSE}"
    exit 1
fi

# Add MCP server tools
echo "Adding MCP server tools..."
TOOL_RESPONSE=$(curl -s -X POST "http://${OPENSEARCH_HOST}:${OPENSEARCH_PORT}/_plugins/_ml/mcp/tools/_register" \
    -H 'Content-Type: application/json' \
    -d '{
    "tools": [
        {
            "type": "ListIndexTool"
        },
        {
            "type": "IndexMappingTool"
        },
        {
            "type": "SearchIndexTool",
            "attributes": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "input": {
                            "index": {
                                "type": "string",
                                "description": "OpenSearch index name."
                            },
                            "query": {
                                "type": "object",
                                "description": "Opensearch query object",
                                "additionalProperties": false
                            }
                        }
                    }
                },
                "required": [
                    "input"
                ],
                "strict": false
            }
        }
    ]
}')

echo "Response from OpenSearch for tool registration:"
echo "${TOOL_RESPONSE}"
