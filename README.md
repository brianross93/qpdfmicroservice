# QPDF Microservice API

This document provides the API specification for the QPDF Microservice, which splits PDF documents based on page ranges.

## Endpoint: `/split`

-   **Method**: `POST`
-   **Description**: Splits a PDF file according to one or more specified page ranges.

### Request

-   **Content-Type**: `multipart/form-data`

-   **Form Fields**:
    1.  `file`: The PDF file to be processed.
    2.  `ranges`: A comma-separated string defining the page ranges.
        -   **Syntax**: The service uses `qpdf` syntax for page ranges. 
        -   **Examples**:
            -   `1-5`: A single range from page 1 to 5.
            -   `1,3,5`: Three separate page ranges (page 1, page 3, page 5).
            -   `1-3,5,7-z`: A mix of ranges. `z` denotes the last page.

### Response

#### Success

-   **Condition**: The `ranges` parameter results in a single output file (e.g., `ranges=1-5`).
    -   **Content-Type**: `application/pdf`
    -   **Body**: The binary content of the resulting PDF file.

-   **Condition**: The `ranges` parameter results in multiple output files (e.g., `ranges=1,3,5`).
    -   **Content-Type**: `application/zip`
    -   **Body**: The binary content of a zip archive containing all resulting PDF files.

#### Error

-   **Content-Type**: `application/json`
-   **Body**: A JSON object describing the error.

-   **Example (400 Bad Request)**:
    ```json
    {
      "error": "No page ranges provided"
    }
    ```

-   **Example (500 Internal Server Error)**:
    ```json
    {
      "error": "An internal error occurred.",
      "details": "Failed to process range '...': {qpdf error details}"
    }
    ```

