const express = require('express');
const path = require('path')
const fs = require('fs')
const { marked } = require('marked')
const markedKatex = require('marked-katex-extension')
const matter = require('gray-matter')

const app = express();
const PORT = 3001;
const mdArray = []

marked.use(markedKatex({
    throwOnError: false
}))

// get array of file tags with path
const contentDir = path.join(__dirname, 'content');
const topics = fs.readdirSync(contentDir);

topics.forEach(topic => {
    const topicDir = path.join(contentDir, topic);
    if (fs.statSync(topicDir).isDirectory()) {
        const lessons = fs.readdirSync(topicDir)

        lessons.forEach(lessonFile => {
            if (path.extname(lessonFile) === ".md") {
                const filePath = path.join(topicDir, lessonFile);
                const fileContent = fs.readFileSync(filePath, 'utf-8')
                const { data } = matter(fileContent)

                mdArray.push({
                    title: data.title,
                    description: data.description || '',
                    url: `/courses/${topic}/${lessonFile.replace('.md', '')}`,
                    tags: data.tags
                });
            }
        })
    }
})

const allTags = mdArray.flatMap(file => file.tags);
const uniqueTags = [... new Set(allTags)].sort()


app.set('view engine', 'ejs')

app.set('views', path.join(__dirname, 'views'));

app.get('/', (req, res) => {
    res.render('home')
})

app.get('/index', (req, res) => {

    res.render('index', {
        blogs: mdArray.sort((a,b) => a.title.localeCompare(b.title)),
        tags: uniqueTags
    });
});

app.get('/index/tag/:tag', (req, res) => {

    const { tag } = req.params

    taggedFiles = mdArray.filter(info => info.tags.includes(tag))

    res.render('index', {
        blogs: taggedFiles.sort((a,b) => a.title.localeCompare(b.title)),
        tags: uniqueTags
    });
});

app.get('/courses/:topic/:lesson', (req, res) => {
    const { topic, lesson } = req.params;
    const filePath = path.join(__dirname, 'content', topic, `${lesson}.md`);

    fs.readFile(filePath, 'utf8', (err, fileContent) => {
        if (err) {
            return res.status(404).send('lesson not found')
        }

        const { data, content } = matter(fileContent);

        const htmlContent = marked.parse(content);

        res.render('lesson', {
            pageTitle: data.title,
            content: htmlContent,
        });
    });
});

app.listen(PORT, () => {
    console.log(`server is running at port ${PORT}`)
})