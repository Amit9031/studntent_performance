# CSE494: Intelligent NoSQL Databases - Viva Preparation Guide
## 45 Comprehensive Viva Questions & Model Answers for Practical Examination

---

### Category 1: SQL vs. NoSQL & Core Concepts

#### Q1: What is a NoSQL database, and how does it differ fundamentally from a Relational (SQL) database?
**Answer:** A NoSQL database is a non-relational database designed to manage semi-structured, unstructured, or rapidly changing data at scale. Unlike SQL databases which enforce rigid tabular schemas, ACID transactions across multiple normalized tables, and SQL queries with foreign keys, NoSQL databases (like MongoDB) utilize flexible document models, horizontal scalability via sharding, and denormalized data designs for high write/read throughput.

#### Q2: What are the four primary categories of NoSQL databases? Which category does MongoDB belong to?
**Answer:** The four categories are:
1. **Document Stores:** (e.g., MongoDB, CouchDB) - Stores data in flexible, self-describing BSON/JSON documents.
2. **Key-Value Stores:** (e.g., Redis, DynamoDB) - Simple associative arrays mapping unique keys to values.
3. **Column-Family Stores:** (e.g., Apache Cassandra, HBase) - Optimized for queries across large volumes of sparse column data.
4. **Graph Databases:** (e.g., Neo4j) - Optimized for interconnected data nodes and relationship edges.  
*MongoDB is a Document-Oriented NoSQL Database.*

#### Q3: What is the CAP Theorem, and where does MongoDB stand in the CAP spectrum?
**Answer:** The CAP Theorem states that a distributed data store can guarantee at most two out of three properties simultaneously:
- **C (Consistency):** Every read receives the most recent write or an error.
- **A (Availability):** Every non-failing node returns a response, without guarantee that it contains the most recent write.
- **P (Partition Tolerance):** The system continues to operate despite network partitions/dropped messages.  
*MongoDB is primarily a **CP** system:* during network partitioning, if the primary replica node cannot reach a majority of replica set members, it steps down to prevent stale/divergent writes, favoring strict consistency over availability until a new primary is elected.

#### Q4: What is BASE in NoSQL, and how does it contrast with ACID?
**Answer:** Traditional SQL adheres to **ACID** (Atomicity, Consistency, Isolation, Durability). NoSQL often adopts **BASE**:
- **Basically Available:** The system ensures availability by spreading data across nodes.
- **Soft State:** Data status may change over time without immediate user interaction due to background replication.
- **Eventual Consistency:** Given sufficient time without new updates, all replicas become consistent.

---

### Category 2: MongoDB Architecture, BSON & Documents

#### Q5: What is BSON, and why does MongoDB use BSON instead of standard JSON?
**Answer:** BSON stands for Binary JSON. It is a binary serialization format used to store documents and make remote procedure calls in MongoDB. It differs from JSON because:
1. It adds support for non-JSON types like `int32`, `int64`, `double`, `date` (BSON Datetime), `ObjectId`, and raw `binData`.
2. It includes length headers and index traversability, allowing the database engine to skip fields without scanning character-by-character, drastically speeding up queries and index evaluation.

#### Q6: What is a Collection and what is a Document in MongoDB?
**Answer:** 
- A **Document** is a single record in MongoDB, analogous to a row in a relational database table. It consists of field-and-value pairs structured in BSON.
- A **Collection** is a grouping of MongoDB documents, analogous to an RDBMS table. Collections do not enforce rigid identical schemas across records unless explicit JSON Schema validation is applied.

#### Q7: What is the maximum size of a BSON document in MongoDB, and why does this limit exist?
**Answer:** The maximum BSON document size is **16 Megabytes**. This limit prevents excessive memory and network bandwidth consumption during queries and prevents inefficient data modeling patterns (such as unbounded nested arrays). For files larger than 16MB, MongoDB provides **GridFS**.

#### Q8: What storage engine does MongoDB use by default, and what are its key advantages?
**Answer:** MongoDB uses the **WiredTiger** storage engine by default. Its advantages include:
1. **Document-level concurrency control:** Multiple clients can write to different documents in the same collection simultaneously without locking the entire collection.
2. **Compression:** Snappy or zlib compression reduces on-disk storage and memory footprint.
3. **Checkpoints & Journaling:** Ensures durability and crash recovery.

---

### Category 3: Data Modeling & Schema Design

#### Q9: What is the difference between Embedding and Referencing in MongoDB?
**Answer:**
- **Embedding:** Storing related data within a single document as nested documents or arrays (e.g., student's `marks` embedded inside the student record). Optimal for 1-to-1 or bounded 1-to-many relationships accessed together in read queries.
- **Referencing:** Storing related data across separate collections and linking them using identifiers (e.g., storing course code strings in `students` and full metadata in `courses`). Optimal for many-to-many relationships or entities that are updated independently to avoid data duplication.

#### Q10: Why did you choose to embed `marks` in the `students` collection in your project?
**Answer:** Because coursework marks are almost always viewed and analyzed in direct conjunction with the student's profile. Embedding guarantees a single atomic read operation, ensures document-level ACID guarantees, and avoids costly multi-collection joins for standard student queries.

#### Q11: When would referencing `courses` be preferred over embedding full course objects in every student?
**Answer:** If full course details (course title, credits, syllabus description, professor) were embedded in 1,000 student documents, changing the course credits would require updating 1,000 separate records (data redundancy and write anomaly). By storing courses in a dedicated `courses` collection and referencing them, course data remains normalized, and joins can be performed via `$lookup` when needed.

#### Q12: How does MongoDB enforce database-level schema validation?
**Answer:** Through the `$jsonSchema` operator configured during `db.create_collection()` or updated via `db.command({"collMod": collection, "validator": ...})`. It validates field types (BSON types), required keys, regex patterns, numeric ranges (minimum/maximum), and array element types at the database engine level, rejecting invalid inserts or updates regardless of client source.

---

### Category 4: PyMongo & Python Integration

#### Q13: What is PyMongo? Does it use an ORM or ODM?
**Answer:** PyMongo is the official, low-level Python driver for MongoDB maintained by MongoDB Inc. It does **not** use an Object-Relational Mapper (ORM) or Object-Document Mapper (ODM) like MongoEngine. Instead, it exposes native Python dictionaries directly corresponding to BSON documents.

#### Q14: Why is it considered a best practice to reuse a single `MongoClient` instance rather than creating a new one per request?
**Answer:** `MongoClient` maintains an internal, thread-safe connection pool (e.g., `minPoolSize=5`, `maxPoolSize=50`). Creating a new `MongoClient` per operation incurs expensive TCP socket handshakes, TLS negotiation, and authentication overhead. Reusing a singleton instance amortizes connection cost and prevents socket exhaustion.

#### Q15: How did you verify the MongoDB connection in Python?
**Answer:** By issuing the administrative ping command:
`client.admin.command('ping')`.
If the server is reachable and active, it returns `{"ok": 1}`. If not, it raises `ConnectionFailure` or `ServerSelectionTimeoutError`.

#### Q16: Why can't raw MongoDB documents always be passed directly to `flask.jsonify()`?
**Answer:** Because BSON documents frequently contain specialized types such as `ObjectId` and `datetime` (BSON Datetime) that standard Python `json.dumps()` does not know how to serialize. They must either be processed through `bson.json_util` or converted using a recursive serializer function that converts datetimes to ISO strings and ObjectIds to strings.

---

### Category 5: PyMongo CRUD Operations

#### Q17: What is the difference between `insert_one()` and `insert_many()`?
**Answer:** 
- `insert_one(doc)`: Inserts a single document and returns an `InsertOneResult` with `inserted_id`.
- `insert_many(list_of_docs, ordered=True/False)`: Sends a batch of documents in a single wire-protocol network trip. Setting `ordered=False` ensures that if one document fails (e.g., duplicate key), MongoDB continues inserting the remaining valid documents.

#### Q18: What is the difference between `update_one()` and `update_many()`?
**Answer:**
- `update_one(filter, update)`: Updates only the *first* document matching the filter criteria, even if thousands match.
- `update_many(filter, update)`: Modifies *all* documents satisfying the filter criteria simultaneously across the collection.

#### Q19: Name four common MongoDB update operators and explain what they do.
**Answer:**
1. `$set`: Assigns a new value to a field (or creates the field if it doesn't exist).
2. `$inc`: Increments/decrements a numeric field by a specified value.
3. `$push`: Appends an item to an existing array.
4. `$addToSet`: Appends an item to an array *only if* it does not already exist, preventing duplicate entries.

#### Q20: How do you update a nested field inside an embedded document in PyMongo?
**Answer:** Using dot notation with the `$set` operator:
`collection.update_one({"_id": 101}, {"$set": {"marks.CSE494": 95.0}})`

#### Q21: What is the purpose of `count_documents()` vs `estimated_document_count()`?
**Answer:**
- `count_documents(filter)`: Accurately counts documents matching a specific query filter by evaluating the query plan.
- `estimated_document_count()`: Obtains an instantaneous count of the entire collection from collection metadata, but cannot take a query filter.

---

### Category 6: Indexing & Query Optimization

#### Q22: What is an index in MongoDB, and what data structure does it use?
**Answer:** An index is a specialized data structure that stores a small portion of the collection's data in an easily traversable form. MongoDB uses **B-Tree (Balanced Tree)** data structures to store ordered keys, enabling fast binary search lookups with $O(\log N)$ time complexity instead of $O(N)$ full scans.

#### Q23: What is the difference between a Single-Field Index and a Compound Index?
**Answer:**
- **Single-Field Index:** Indexes keys on a single document attribute (e.g. `students.create_index("department")`).
- **Compound Index:** Indexes keys across multiple attributes in a specified order and direction (e.g. `students.create_index([("department", 1), ("attendance", -1)])`). It optimizes queries filtering on department AND sorting on attendance.

#### Q24: What is the Prefix Rule in compound indexes?
**Answer:** A compound index on `(A, B, C)` can support queries on:
- `(A)`
- `(A, B)`
- `(A, B, C)`
However, it cannot efficiently support queries on `(B)` or `(C)` alone because the index is sorted primarily by `A`.

#### Q25: What is a Unique Index?
**Answer:** An index created with `unique=True` (e.g. `email`). MongoDB's storage engine rejects any insert or update that would introduce duplicate index keys, raising a `DuplicateKeyError`.

#### Q26: What is a Text Index in MongoDB?
**Answer:** A text index (e.g., `[("name", "text"), ("email", "text")]`) supports text search queries inside string fields using the `$text` and `$search` operators, supporting stemming and case-insensitive word matching.

#### Q27: What is `explain("executionStats")`, and what key metrics did your benchmark analyze?
**Answer:** `explain("executionStats")` runs the query and returns diagnostic information from the MongoDB query planner. Key metrics:
1. `winningPlan.stage`: Shows whether MongoDB performed a `COLLSCAN` (full collection scan) or `IXSCAN` (index scan).
2. `totalDocsExamined`: Number of actual documents read from disk/cache.
3. `totalKeysExamined`: Number of index keys traversed.
4. `nReturned`: Number of documents returned to the client.
5. `executionTimeMillis`: Total server execution time in milliseconds.

#### Q28: What is a "Covered Query"?
**Answer:** A covered query is a query where all queried fields are in the index and all projected fields are returned directly from the index without reading any document from disk (`totalDocsExamined = 0`). It provides the highest possible read performance.

#### Q29: Does adding indexes always make a database faster? What are the trade-offs?
**Answer:** No. While indexes significantly accelerate read queries, they introduce two trade-offs:
1. **Write Overhead:** Every `insert`, `update`, or `delete` must also update all associated B-Tree index structures, increasing write latency.
2. **Storage and RAM Consumption:** Indexes consume disk space and must fit into WiredTiger's RAM cache for optimal performance. Unused or redundant indexes waste resources.

---

### Category 7: MongoDB Aggregation Framework

#### Q30: What is the MongoDB Aggregation Framework?
**Answer:** The Aggregation Framework is an execution pipeline modeled on the concept of data processing pipelines. Documents enter a multi-stage pipeline where successive stages transform, filter, group, project, join, and compute aggregates over the stream of documents directly on the server.

#### Q31: What is the purpose of `$match` and where should it ideally be placed in a pipeline?
**Answer:** `$match` filters documents to allow only those matching specified criteria to pass to the next stage. It should ideally be placed at the **very beginning** of the pipeline so it can leverage indexes and reduce the number of documents processed by downstream stages.

#### Q32: What does the `$project` stage do?
**Answer:** `$project` reshapes documents by including specific fields, excluding fields (like `_id: 0`), renaming fields, or computing new calculated fields using aggregation expressions.

#### Q33: How does `$group` work, and what is the role of `_id` in `$group`?
**Answer:** `$group` collapses multiple input documents into summary documents based on a grouping key defined by `_id`. For example, `{"_id": "$department", "avg_marks": {"$avg": "$marks"}}` groups documents having the same department value together. Setting `_id: null` computes aggregate metrics over the entire collection.

#### Q34: How did you calculate the average marks for a student when `marks` is an embedded key-value document?
**Answer:** Since `$avg` cannot be applied directly to an embedded document with arbitrary course keys, we use `$objectToArray: "$marks"` to convert the embedded document into an array of `{k: "course", v: score}` objects. Then we compute the average across values using `{"$avg": "$marks_array.v"}`.

#### Q35: What does `$unwind` do, and what pipeline did you use it in?
**Answer:** `$unwind` deconstructs an array field from the input documents to output a document for *each* element in the array. We used it in:
- **Pipeline 6 (Skill Distribution):** To break the `skills` array into individual skill records and count their overall occurrences.
- **Pipeline 5 (Course Statistics):** To unwind the key-value marks array so scores can be grouped by course code.

#### Q36: What is `$lookup` in MongoDB, and what are its four required parameters?
**Answer:** `$lookup` performs a left outer join to an unsharded collection in the same database to filter in documents from the "joined" collection. Its four parameters are:
1. `from`: Target collection to join with (e.g., `"courses"`).
2. `localField`: Field from the input documents (e.g., `"_id"` from unwound marks).
3. `foreignField`: Field from the target collection (e.g., `"_id"` of courses).
4. `as`: Name of the new array field to output the joined documents (e.g., `"course_info"`).

#### Q37: What is the purpose of `$facet`?
**Answer:** `$facet` allows executing multiple aggregation pipelines within a single stage on the same set of input documents. In Pipeline 9, we used `$facet` to simultaneously calculate overall system metrics (total students, average marks) and count at-risk students in a single database round-trip.

#### Q38: How does `$switch` work in Pipeline 7?
**Answer:** `$switch` performs multi-branch conditional logic analogous to `if-else if-else`. It evaluates an array of `case` expressions with corresponding `then` outcomes and falls back to a `default` value, allowing us to categorize students into academic tiers ("Excellent", "Good", "Average", "Needs Improvement").

---

### Category 8: System Architecture, Testing & Machine Learning

#### Q39: What is the role of Flask in your project?
**Answer:** Flask serves as the lightweight Python WSGI web backend. It provides:
1. Routing and request handling for both browser-based HTML templates and REST API endpoints.
2. Jinja2 template rendering for server-side HTML.
3. Separation of concerns by delegating business logic and database queries to service modules (`StudentService`, `CourseService`, `AnalyticsService`).

#### Q40: What features did your machine learning model use to predict academic risk?
**Answer:** The Scikit-Learn `RandomForestClassifier` uses five engineered features:
1. `attendance` (Float percentage)
2. `avg_marks` (Float mean academic score)
3. `semester` (Integer cohort level)
4. `num_courses` (Integer count of enrolled subjects)
5. `num_skills` (Integer count of technical skills)

#### Q41: Why should machine learning predictions be treated as an advisory tool rather than an absolute truth?
**Answer:** Because models trained on synthetic or historical data can suffer from distribution drift, dataset bias, and lack access to unquantified qualitative human factors (e.g., medical leave, family emergencies). In our project, deterministic rule-based evaluation provides transparent primary criteria, while the ML model provides secondary probabilistic risk attribution.

#### Q42: How did you ensure test isolation in `pytest`?
**Answer:** By configuring a dedicated test database (`student_analytics_test`) in `tests/conftest.py`. The fixture sets up schema validation, seeds test data, runs all 36 test assertions against the isolated test database, and drops the test database during session teardown, ensuring normal project data is never altered.

#### Q43: What is the purpose of `.env` and `config.py` in your application?
**Answer:** To adhere to Twelve-Factor App principles. Configuration variables (such as `MONGODB_URI`, `DATABASE_NAME`, `PORT`, `SECRET_KEY`) are kept out of source code and loaded dynamically from `.env`, preventing credential leakage and allowing environment portability.

#### Q44: What happens if a client attempts to delete a course that students are currently enrolled in?
**Answer:** The `delete_course` method checks referential integrity using `db["students"].count_documents({"marks.<course_code>": {"$exists": True}})`. If any student has marks recorded for that course, the deletion is rejected with a `400 Bad Request` and an informative error message.

#### Q45: How does your application protect against NoSQL Injection attacks?
**Answer:** By:
1. Using strict application-level payload validation (`validate_student_payload`) to sanitize data types and enforce permitted regex patterns before queries are built.
2. Using parameterized MongoDB query filter dictionaries instead of dynamically concatenating client strings into raw JavaScript or `$where` expressions.
3. Enforcing database-level JSON Schema validation to reject malformed records.
