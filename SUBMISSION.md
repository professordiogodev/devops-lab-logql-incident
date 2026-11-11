# Submission

Fork URL: <!-- paste the URL of your fork here -->

## Files to commit

- [ ] `queries.yaml`: your ten LogQL expressions
- [ ] `REPORT.md`: the incident report, written from your queries

## Questions

Answer in your own words. Where a question asks for output, paste it in a code block.

### Q1. Paste your queries for questions 1 and 4. Explain, in your own words, the difference between a **label** (`{service="orders"}`), a **line filter** (`|= "card_declined"`) and a **parsed field** (`| json | level="error"`). Which is fastest, and why does Loki not index the line itself?

**Your answer:**

<!-- replace this line with your answer -->

### Q2. Paste your query for the 95th percentile of `duration_ms`. What does `unwrap` do, and why is the result different from the average? Which function turned a stream of lines into numbers?

**Your answer:**

<!-- replace this line with your answer -->

### Q3. Question 7 reads text that is not JSON. Paste your `pattern` or `regexp` query. When is `pattern` better than `regexp`, and why should the best answer be "log JSON in the first place"?

**Your answer:**

<!-- replace this line with your answer -->

### Q4. Paste your question 9 query. Why does an aggregation by `trace_id` risk "too many series", and what did you do about it? What is high cardinality, and which of these would you never make a label: `service`, `level`, `trace_id`, `customer`?

**Your answer:**

<!-- replace this line with your answer -->

### Q5. Paste your REPORT.md. Which three facts (service, window, size) are the heart of it? Which of your queries would you turn into a log-based alert, and what could you NOT know from logs alone that metrics or traces would have told you?

**Your answer:**

<!-- replace this line with your answer -->

### Q6. Paste the output of `./verify.sh`. It must end with **ALL CHECKS PASSED**.

**Your answer:**

<!-- replace this line with your answer -->

### Q7. **Tear down.** Paste the output of `./verify-teardown.sh`. It must end with **TEARDOWN VERIFIED**.

**Your answer:**

<!-- replace this line with your answer -->
