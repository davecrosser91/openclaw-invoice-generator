import { Type } from "@sinclair/typebox";

interface PluginConfig {
  apiUrl: string;
  strapiUrl: string;
  bearerToken: string;
  maxRetries: number;
}

// --- Strapi Response Types ---

interface StrapiAttributes {
  [key: string]: any;
}

interface StrapiEntry {
  id: number;
  attributes: StrapiAttributes;
}

interface StrapiResponse {
  data: StrapiEntry | StrapiEntry[] | null;
  meta?: { pagination?: { page: number; pageSize: number; pageCount: number; total: number } };
}

// --- Invoice Data Types (from DocumentGenerator API) ---

interface InvoiceData {
  seller_name?: string;
  buyer_name?: string;
  invoice_number?: string;
  invoice_date?: string;
  products?: Array<{
    product_name: string;
    quantity: number;
    unit_price: number;
    line_total: number;
    taxrate?: string;
  }>;
  subtotal?: number;
  tax_amount?: number;
  grand_total?: number;
}

// --- Strapi Content Types ---

interface StrapiInvoice {
  invoicenumber: string;
  dateofinvoice: string; // ISO 8601
  dateofdeliveryorservice?: string;
  subtotal: number;
  taxes: number;
  total: number;
  validated: boolean;
  // Relations (populated)
  products?: { data: StrapiEntry[] };
  buyer?: { data: StrapiEntry | null };
  seller?: { data: StrapiEntry | null };
  story?: { data: StrapiEntry | null };
  pdfinvoice?: { data: StrapiEntry[] };
}

interface StrapiProduct {
  name: string;
  quantity: number;
  price: number; // unit price
  tax: number; // tax amount for this line
  taxrate: string; // "0%", "7%", or "19%"
  unity: string; // "Stück", "Set", "Paket", "Stunde", etc.
  seller?: { data: StrapiEntry | null };
  invoice?: { data: StrapiEntry[] };
}

interface StrapiBuyer {
  name: string;
  street: string;
  postalcode: string;
  city: string;
  email?: string;
  phone?: string;
  fax?: string;
  iban?: string;
  bic?: string;
  employee?: string;
  customerid?: string;
  ifforeigntaxidentifier?: string;
  website?: string;
}

interface StrapiSeller {
  name: string;
  street: string;
  postalcode: string;
  city: string;
  email?: string;
  phone?: string;
  fax?: string;
  iban?: string;
  bic?: string;
  employee?: string;
  taxidentifier?: string;
  website?: string;
}

interface StrapiTemplate {
  name: string;
  html: string; // HTML with placeholders
  products: number; // product row count
  language: string;
  validated: boolean;
  doctype?: "invoice" | "letter" | "form";
}

interface StrapiPdfInvoice {
  pdf?: { data: StrapiEntry | null }; // media
  logo?: { data: StrapiEntry | null }; // media (image)
  logo_position?: any; // JSON
  filled_html?: string;
  precisecontent?: Record<string, string>; // placeholder→value map
  validated?: boolean;
  comments?: string;
  isReal?: boolean;
  evaluation_count?: number;
  avg_quality_score?: number;
  fooled_ratio?: number;
  invoice?: { data: StrapiEntry | null };
  buyer?: { data: StrapiEntry | null };
  seller?: { data: StrapiEntry | null };
  template?: { data: StrapiEntry | null };
  story?: { data: StrapiEntry | null };
}

// --- Strapi Endpoints ---

const ENDPOINTS = {
  invoices: "/api/invoices",
  products: "/api/products",
  buyers: "/api/buyers",
  sellers: "/api/sellers",
  templates: "/api/templates",
  pdfInvoices: "/api/pdf-invoices",
  stories: "/api/stories",
  entities: "/api/entities",
  imagePairs: "/api/image-pairs",
  evaluations: "/api/evaluations",
  upload: "/api/upload",
  uploadFiles: "/api/upload/files",
} as const;

// --- Validation Helpers ---

function validateInvoiceMath(data: InvoiceData): string[] {
  const issues: string[] = [];

  if (!data.products || data.products.length === 0) {
    issues.push("No products found in invoice data");
    return issues;
  }

  for (const product of data.products) {
    const expected = product.quantity * product.unit_price;
    if (Math.abs(product.line_total - expected) > 0.01) {
      issues.push(
        `Line total mismatch for "${product.product_name}": ` +
          `${product.quantity} x ${product.unit_price} = ${expected}, got ${product.line_total}`
      );
    }
  }

  if (data.subtotal !== undefined) {
    const expectedSubtotal = data.products.reduce(
      (sum, p) => sum + p.line_total,
      0
    );
    if (Math.abs(data.subtotal - expectedSubtotal) > 0.01) {
      issues.push(
        `Subtotal mismatch: sum of line totals = ${expectedSubtotal}, got ${data.subtotal}`
      );
    }
  }

  if (
    data.grand_total !== undefined &&
    data.subtotal !== undefined &&
    data.tax_amount !== undefined
  ) {
    const expectedTotal = data.subtotal + data.tax_amount;
    if (Math.abs(data.grand_total - expectedTotal) > 0.01) {
      issues.push(
        `Grand total mismatch: ${data.subtotal} + ${data.tax_amount} = ${expectedTotal}, got ${data.grand_total}`
      );
    }
  }

  return issues;
}

function validateRequiredFields(data: InvoiceData): string[] {
  const issues: string[] = [];
  const required = [
    "seller_name",
    "buyer_name",
    "invoice_number",
    "invoice_date",
    "products",
    "grand_total",
  ];

  for (const field of required) {
    if (!(field in data) || data[field as keyof InvoiceData] === undefined) {
      issues.push(`Missing required field: ${field}`);
    }
  }

  return issues;
}

// --- Strapi Helper ---

function strapiHeaders(bearerToken: string, json = false): Record<string, string> {
  const headers: Record<string, string> = {
    Authorization: `Bearer ${bearerToken}`,
  };
  if (json) {
    headers["Content-Type"] = "application/json";
  }
  return headers;
}

function toolResult(data: any) {
  return {
    content: [{ type: "text" as const, text: JSON.stringify(data, null, 2) }],
  };
}

// --- Plugin Registration ---

export default function (api: any) {
  const config = api.pluginConfig as PluginConfig;

  // ===========================
  // STRAPI QUERY TOOLS
  // ===========================

  // Tool: Query Strapi
  api.registerTool({
    name: "strapi_query",
    description:
      "Query any Strapi content type. Supports filtering, population of relations, " +
      "pagination, and sorting. Use this to list, search, or fetch invoices, products, " +
      "buyers, sellers, templates, PDF invoices, stories, evaluations, and image pairs.",
    parameters: Type.Object({
      content_type: Type.String({
        description:
          "Strapi content type to query: invoices, products, buyers, sellers, " +
          "templates, pdf-invoices, stories, entities, image-pairs, evaluations",
        enum: [
          "invoices", "products", "buyers", "sellers", "templates",
          "pdf-invoices", "stories", "entities", "image-pairs", "evaluations",
        ],
      }),
      id: Type.Optional(
        Type.Number({ description: "Specific entry ID to fetch. Omit to list/search." })
      ),
      filters: Type.Optional(
        Type.String({
          description:
            'Strapi filter query string (without leading ?). Example: ' +
            '"filters[name][$containsi]=Schunk&filters[validated][$eq]=true"',
        })
      ),
      populate: Type.Optional(
        Type.String({
          description:
            'Strapi populate query string. Example: ' +
            '"populate[products][fields][0]=name&populate[buyer][fields][0]=name"' +
            ' or "populate=*" for all relations.',
        })
      ),
      sort: Type.Optional(
        Type.String({
          description: 'Sort order. Example: "sort=id:desc" or "sort=total:asc"',
        })
      ),
      page: Type.Optional(
        Type.Number({ description: "Page number for pagination (default: 1)", default: 1 })
      ),
      page_size: Type.Optional(
        Type.Number({ description: "Page size (default: 25, max: 100)", default: 25 })
      ),
    }),
    async execute(
      _id: string,
      params: {
        content_type: string;
        id?: number;
        filters?: string;
        populate?: string;
        sort?: string;
        page?: number;
        page_size?: number;
      }
    ) {
      const endpoint = `/api/${params.content_type}`;
      let url = `${config.strapiUrl}${endpoint}`;

      if (params.id) {
        url += `/${params.id}`;
      }

      const queryParts: string[] = [];
      if (params.filters) queryParts.push(params.filters);
      if (params.populate) queryParts.push(params.populate);
      if (params.sort) queryParts.push(params.sort);
      queryParts.push(`pagination[page]=${params.page ?? 1}`);
      queryParts.push(`pagination[pageSize]=${params.page_size ?? 25}`);

      if (queryParts.length > 0) {
        url += "?" + queryParts.join("&");
      }

      const response = await fetch(url, {
        headers: strapiHeaders(config.bearerToken),
      });

      if (!response.ok) {
        return toolResult({
          error: "strapi_query_error",
          status: response.status,
          message: await response.text(),
          url,
        });
      }

      return toolResult(await response.json());
    },
  });

  // Tool: Create/Update Strapi entry
  api.registerTool({
    name: "strapi_mutate",
    description:
      "Create, update, or delete a Strapi entry. Supports all content types. " +
      "For relations, use { connect: [id] } or { disconnect: [id] } syntax.",
    parameters: Type.Object({
      content_type: Type.String({
        description: "Strapi content type",
        enum: [
          "invoices", "products", "buyers", "sellers", "templates",
          "pdf-invoices", "stories", "entities", "image-pairs", "evaluations",
        ],
      }),
      operation: Type.String({
        description: "Operation to perform",
        enum: ["create", "update", "delete"],
      }),
      id: Type.Optional(
        Type.Number({ description: "Entry ID (required for update/delete)" })
      ),
      data: Type.Optional(
        Type.Any({
          description:
            "Data payload. Wrap in Strapi format: { invoicenumber: '...', total: 100, " +
            "buyer: { connect: [84] } }. Do NOT wrap in { data: ... } — this is done automatically.",
        })
      ),
    }),
    async execute(
      _id: string,
      params: {
        content_type: string;
        operation: string;
        id?: number;
        data?: any;
      }
    ) {
      const endpoint = `/api/${params.content_type}`;
      let url = `${config.strapiUrl}${endpoint}`;

      if (params.operation === "update" || params.operation === "delete") {
        if (!params.id) {
          return toolResult({ error: "ID is required for update/delete operations" });
        }
        url += `/${params.id}`;
      }

      const method =
        params.operation === "create"
          ? "POST"
          : params.operation === "update"
          ? "PUT"
          : "DELETE";

      const fetchOptions: RequestInit = {
        method,
        headers: strapiHeaders(config.bearerToken, method !== "DELETE"),
      };

      if (method !== "DELETE" && params.data) {
        fetchOptions.body = JSON.stringify({ data: params.data });
      }

      const response = await fetch(url, fetchOptions);

      if (!response.ok) {
        return toolResult({
          error: `strapi_${params.operation}_error`,
          status: response.status,
          message: await response.text(),
        });
      }

      if (method === "DELETE") {
        return toolResult({ success: true, deleted_id: params.id });
      }

      return toolResult(await response.json());
    },
  });

  // Tool: Get dataset statistics
  api.registerTool({
    name: "strapi_stats",
    description:
      "Get statistics about the invoice dataset: total counts for invoices, " +
      "PDF invoices, templates, products, buyers, sellers, evaluations.",
    parameters: Type.Object({}),
    async execute() {
      const types = [
        "invoices", "products", "buyers", "sellers",
        "templates", "pdf-invoices", "stories", "evaluations", "image-pairs",
      ];

      const results: Record<string, number | string> = {};

      await Promise.all(
        types.map(async (type) => {
          const response = await fetch(
            `${config.strapiUrl}/api/${type}?pagination[pageSize]=1`,
            { headers: strapiHeaders(config.bearerToken) }
          );
          if (response.ok) {
            const json = await response.json();
            results[type] = json.meta?.pagination?.total ?? "unknown";
          } else {
            results[type] = `error (${response.status})`;
          }
        })
      );

      return toolResult({ dataset_statistics: results });
    },
  });

  // Tool: Get PDF download URL
  api.registerTool({
    name: "strapi_get_pdf_url",
    description:
      "Get the download URL for a PDF invoice by its ID. " +
      "Returns the Strapi media URL that can be used to download the PDF.",
    parameters: Type.Object({
      pdf_invoice_id: Type.Number({
        description: "The PDF invoice ID in Strapi",
      }),
    }),
    async execute(_id: string, params: { pdf_invoice_id: number }) {
      const url =
        `${config.strapiUrl}/api/pdf-invoices/${params.pdf_invoice_id}` +
        "?populate[pdf][fields][0]=url&populate[pdf][fields][1]=name";

      const response = await fetch(url, {
        headers: strapiHeaders(config.bearerToken),
      });

      if (!response.ok) {
        return toolResult({
          error: "fetch_error",
          status: response.status,
        });
      }

      const json: StrapiResponse = await response.json();
      const entry = json.data as StrapiEntry;
      const pdfData = entry?.attributes?.pdf?.data;

      if (!pdfData) {
        return toolResult({
          error: "no_pdf",
          message: `PDF invoice ${params.pdf_invoice_id} has no PDF file attached`,
        });
      }

      const pdfUrl = pdfData.attributes?.url;
      return toolResult({
        pdf_invoice_id: params.pdf_invoice_id,
        pdf_name: pdfData.attributes?.name,
        pdf_url: `${config.strapiUrl}${pdfUrl}`,
        relative_url: pdfUrl,
      });
    },
  });

  // ===========================
  // INVOICE GENERATION TOOLS
  // ===========================

  // Tool: Generate invoice data
  api.registerTool({
    name: "generate_invoice_data",
    description:
      "Generate synthetic invoice data using the DocumentGenerator LLM pipeline. " +
      "Returns structured invoice JSON with seller, buyer, products, and totals.",
    parameters: Type.Object({
      num_products: Type.Number({
        description: "Number of line items (1-50)",
        default: 5,
        minimum: 1,
        maximum: 50,
      }),
      language: Type.String({
        description: "Invoice language: 'de' (German) or 'en' (English)",
        default: "de",
        enum: ["de", "en"],
      }),
    }),
    async execute(
      _id: string,
      params: { num_products: number; language: string }
    ) {
      const url = new URL("/create_invoice", config.apiUrl);
      url.searchParams.set("num_products", String(params.num_products));
      url.searchParams.set("language", params.language);
      url.searchParams.set("llm_model", "gpt-5.1");

      const response = await fetch(url.toString());

      if (!response.ok) {
        return toolResult({
          error: "api_error",
          status: response.status,
          message: await response.text(),
        });
      }

      const invoiceData = await response.json();

      const fieldIssues = validateRequiredFields(invoiceData);
      const mathIssues = validateInvoiceMath(invoiceData);
      const allIssues = [...fieldIssues, ...mathIssues];

      return toolResult({
        success: allIssues.length === 0,
        invoice_data: invoiceData,
        validation: {
          issues: allIssues,
          field_check: fieldIssues.length === 0 ? "pass" : "fail",
          math_check: mathIssues.length === 0 ? "pass" : "fail",
        },
      });
    },
  });

  // Tool: Post invoice to Strapi and generate PDF
  api.registerTool({
    name: "create_invoice_pdf",
    description:
      "Post invoice data to Strapi and generate a PDF. " +
      "Takes the invoice data from generate_invoice_data and produces a PDF invoice.",
    parameters: Type.Object({
      invoice_data: Type.Any({
        description: "Invoice data JSON from generate_invoice_data",
      }),
    }),
    async execute(_id: string, params: { invoice_data: any }) {
      // Post invoice data to Strapi
      const postResponse = await fetch(
        `${config.apiUrl}/post_invoice_data_to_strapi`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            invoice_data: params.invoice_data,
            bearer_token: config.bearerToken,
          }),
        }
      );

      if (!postResponse.ok) {
        return toolResult({
          error: "strapi_post_error",
          status: postResponse.status,
          message: await postResponse.text(),
        });
      }

      const { pdf_invoice_id } = await postResponse.json();

      // Generate PDF
      const formData = new FormData();
      formData.append("pdf_invoice_id", String(pdf_invoice_id));
      formData.append("bearer_token", config.bearerToken);
      formData.append("pdf_params", "{}");

      const pdfResponse = await fetch(
        `${config.apiUrl}/create_pdf_for_pdf_invoice_entry`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (!pdfResponse.ok) {
        return toolResult({
          error: "pdf_generation_error",
          status: pdfResponse.status,
          message: await pdfResponse.text(),
          pdf_invoice_id,
          hint: "PDF generation failed. Check Chromium on server.",
        });
      }

      // Verify in Strapi
      const verifyResponse = await fetch(
        `${config.strapiUrl}/api/pdf-invoices/${pdf_invoice_id}` +
          "?populate[pdf][fields][0]=url&populate[invoice][fields][0]=invoicenumber" +
          "&populate[buyer][fields][0]=name&populate[seller][fields][0]=name",
        { headers: strapiHeaders(config.bearerToken) }
      );

      let verification = null;
      if (verifyResponse.ok) {
        const verifyJson: StrapiResponse = await verifyResponse.json();
        const entry = verifyJson.data as StrapiEntry;
        verification = {
          has_pdf: !!entry?.attributes?.pdf?.data,
          has_invoice: !!entry?.attributes?.invoice?.data,
          has_buyer: !!entry?.attributes?.buyer?.data,
          has_seller: !!entry?.attributes?.seller?.data,
        };
      }

      return toolResult({
        success: true,
        pdf_invoice_id,
        message: `Invoice PDF created (ID: ${pdf_invoice_id})`,
        verification,
      });
    },
  });

  // Tool: Full pipeline with verification and retry
  api.registerTool({
    name: "generate_verified_invoice",
    description:
      "Full invoice generation pipeline: generates data, validates, creates PDF, " +
      "verifies in Strapi, and retries automatically on failure. Use this for reliable invoice creation.",
    parameters: Type.Object({
      num_products: Type.Number({
        description: "Number of line items (1-50)",
        default: 5,
        minimum: 1,
        maximum: 50,
      }),
      language: Type.String({
        description: "Invoice language: 'de' or 'en'",
        default: "de",
        enum: ["de", "en"],
      }),
      max_retries: Type.Number({
        description: "Maximum retry attempts",
        default: 3,
        minimum: 1,
        maximum: 5,
      }),
    }),
    async execute(
      _id: string,
      params: { num_products: number; language: string; max_retries: number }
    ) {
      const maxRetries = params.max_retries ?? config.maxRetries ?? 3;
      const attempts: Array<{
        attempt: number;
        error_type: string;
        details: string;
      }> = [];

      for (let attempt = 1; attempt <= maxRetries; attempt++) {
        // Step 1: Generate invoice data
        const genUrl = new URL("/create_invoice", config.apiUrl);
        genUrl.searchParams.set("num_products", String(params.num_products));
        genUrl.searchParams.set("language", params.language);
        genUrl.searchParams.set("llm_model", "gpt-5.1");

        let invoiceData: InvoiceData;
        try {
          const genResponse = await fetch(genUrl.toString());
          if (!genResponse.ok) {
            attempts.push({
              attempt,
              error_type: "api_error",
              details: `Generate returned ${genResponse.status}`,
            });
            continue;
          }
          invoiceData = await genResponse.json();
        } catch (e: any) {
          attempts.push({ attempt, error_type: "network_error", details: e.message });
          continue;
        }

        // Step 2: Validate
        const fieldIssues = validateRequiredFields(invoiceData);
        const mathIssues = validateInvoiceMath(invoiceData);

        if (fieldIssues.length > 0) {
          attempts.push({ attempt, error_type: "missing_fields", details: fieldIssues.join("; ") });
          continue;
        }

        if (mathIssues.length > 0) {
          attempts.push({ attempt, error_type: "math_error", details: mathIssues.join("; ") });
          continue;
        }

        // Step 3: Post to Strapi
        let pdfInvoiceId: number;
        try {
          const postResponse = await fetch(
            `${config.apiUrl}/post_invoice_data_to_strapi`,
            {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                invoice_data: invoiceData,
                bearer_token: config.bearerToken,
              }),
            }
          );

          if (!postResponse.ok) {
            attempts.push({
              attempt,
              error_type: "strapi_error",
              details: `Post returned ${postResponse.status}`,
            });
            continue;
          }

          const postResult = await postResponse.json();
          pdfInvoiceId = postResult.pdf_invoice_id;
        } catch (e: any) {
          attempts.push({ attempt, error_type: "network_error", details: e.message });
          continue;
        }

        // Step 4: Generate PDF (with sub-retry)
        let pdfSuccess = false;
        for (let pdfAttempt = 1; pdfAttempt <= 2; pdfAttempt++) {
          try {
            const formData = new FormData();
            formData.append("pdf_invoice_id", String(pdfInvoiceId));
            formData.append("bearer_token", config.bearerToken);
            formData.append("pdf_params", "{}");

            const pdfResponse = await fetch(
              `${config.apiUrl}/create_pdf_for_pdf_invoice_entry`,
              { method: "POST", body: formData }
            );

            if (pdfResponse.ok) {
              pdfSuccess = true;
              break;
            }
          } catch {
            // retry
          }

          await new Promise((resolve) => setTimeout(resolve, 5000));
        }

        if (!pdfSuccess) {
          attempts.push({
            attempt,
            error_type: "pdf_error",
            details: "PDF generation failed after 2 sub-attempts",
          });
          continue;
        }

        // Step 5: Verify in Strapi
        let verified = false;
        try {
          const verifyResponse = await fetch(
            `${config.strapiUrl}/api/pdf-invoices/${pdfInvoiceId}` +
              "?populate[pdf][fields][0]=url" +
              "&populate[invoice][fields][0]=invoicenumber" +
              "&populate[buyer][fields][0]=name" +
              "&populate[seller][fields][0]=name",
            { headers: strapiHeaders(config.bearerToken) }
          );

          if (verifyResponse.ok) {
            const verifyJson: StrapiResponse = await verifyResponse.json();
            const entry = verifyJson.data as StrapiEntry;
            const hasPdf = !!entry?.attributes?.pdf?.data;
            const hasInvoice = !!entry?.attributes?.invoice?.data;
            const hasBuyer = !!entry?.attributes?.buyer?.data;
            const hasSeller = !!entry?.attributes?.seller?.data;
            verified = hasPdf && hasInvoice && hasBuyer && hasSeller;

            if (!verified) {
              const missing = [];
              if (!hasPdf) missing.push("pdf");
              if (!hasInvoice) missing.push("invoice");
              if (!hasBuyer) missing.push("buyer");
              if (!hasSeller) missing.push("seller");
              attempts.push({
                attempt,
                error_type: "verification_error",
                details: `Missing in Strapi: ${missing.join(", ")}`,
              });
              continue;
            }
          }
        } catch {
          // Verification fetch failed, but PDF was created — consider it a soft pass
          verified = true;
        }

        // Success
        return toolResult({
          success: true,
          pdf_invoice_id: pdfInvoiceId,
          invoice_number: invoiceData.invoice_number,
          seller: invoiceData.seller_name,
          buyer: invoiceData.buyer_name,
          products: invoiceData.products?.length,
          grand_total: invoiceData.grand_total,
          language: params.language,
          verified,
          attempts: attempt,
          attempt_log: attempts.length > 0 ? attempts : undefined,
        });
      }

      // All retries exhausted
      return toolResult({
        success: false,
        error: "max_retries_exhausted",
        total_attempts: maxRetries,
        attempt_log: attempts,
        suggestion:
          attempts[attempts.length - 1]?.error_type === "pdf_error"
            ? "Check server Chromium installation and PUPPETEER_EXECUTABLE_PATH"
            : attempts[attempts.length - 1]?.error_type === "verification_error"
            ? "Strapi relations may be broken. Check manually with strapi_query tool."
            : "LLM may be producing inconsistent output. Try a different model or fewer products.",
      });
    },
  });
}
