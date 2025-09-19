const express = require('express');
const path = require('path')
const fs = require('fs')
const { marked } = require('marked')
const markedKatex = require('marked-katex-extension')
const matter = require('gray-matter')
const { exec } = require('child_process');

const app = express();
const PORT = 8080;
const mdArray = []

app.use(express.static(path.join(__dirname, 'content')))

marked.use(markedKatex({
    throwOnError: false
}))

marked.setOptions({
    // breaks: true, // This is the magic option
    gfm: true,    // Use GitHub Flavored Markdown
    pedantic: false // Don't be strict about minor markdown errors
});

let recentChangesCache = [];

const gitCommand = "git log -1 --name-status --pretty=format: -- content/"

exec(gitCommand, (error, stdout, stderr) => {
    if (error) {
        console.warn("couldnt run git command, is this a repo? recent changes wont be displayed.")
        return
    }

    const allChanges = [];
    const changedFiles = stdout.trim().split('\n')

    changedFiles.forEach(line => {
        if (!line) return

        const [status, filePath] = line.split('\t')

        allChanges.push({
            title: filePath.split('/')[2],
            url: "/courses/" + filePath.replace('.md', '').replace('content/', ''),
            stated: status === 'A' ? 'Added' : 'Modified'
        })
    })

    recentChangesCache = allChanges;
    // console.log("changes made:", recentChangesCache)
})

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
    res.render('home', {
        changes: recentChangesCache,
        date: "67/69/420"
    })
})

app.get('/index', (req, res) => {

    res.render('index', {
        blogs: mdArray.sort((a, b) => a.title.localeCompare(b.title)),
        tags: uniqueTags
    });
});

app.get('/index/tag/:tag', (req, res) => {

    const { tag } = req.params

    taggedFiles = mdArray.filter(info => info.tags.includes(tag))

    res.render('index', {
        blogs: taggedFiles.sort((a, b) => a.title.localeCompare(b.title)),
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
        
        const regex_keywords =  /(?<!`)`([^`]+)`(?!`)/g

        const contentWithKeywords = content.replaceAll(regex_keywords, (fullMatch, innerText) => {
            if (innerText.includes('`')) { return innerText }
            return `<b>${innerText}</b>`
        })

        const regex_notes = /\+\+([\s\S]+?)\+\+/g // match lazily 

        const htmlContent = marked.parse(contentWithKeywords).replaceAll(regex_notes, (fullMatch, innerText) => {
            const lines = innerText.trim().split('\n');
            let commentParts = [];
            let contentParts = [];
            for (const line of lines) {
                if (line.includes('/\\')) {
                    commentParts.push(line.replace('/\\', '').trim());
                } else {
                    contentParts.push(line);
                }
            }
// style="position: absolute;left: 100%; width: 200px; margin-left: 30px"
            return `
                <div class="sidenote-container">
                    <div class="sidenote-margin">
                        ${commentParts.join(' ')}
                    </div>
                    <div class="sidenote-main">
                        ${contentParts.join('\n')}
                    </div>
                </div>
                `
        })

        res.render('lesson', {
            pageTitle: data.title,
            content: htmlContent,
        });
    });
});

app.listen(PORT, () => {
    console.log(`server is running at port ${PORT}`)
})