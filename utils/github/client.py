from __future__ import annotations
from typing import TYPE_CHECKING

import os
import yarl
import asyncio
import dateparser

import disnake
from disnake.ext import commands

import utils

if TYPE_CHECKING:
    from main import Okiyu

__all__ = ('GistContent', 'GithubClient',)


class GithubError(commands.CommandError):
    pass


class GistContent:
    def __init__(self, argument: str):
        try:
            block, code = argument.split('\n', 1)
        except ValueError:
            self.source = argument
            self.language = None
        else:
            if not block.startswith('```') and not code.endswith('```'):
                self.source = argument
                self.language = None
            else:
                self.language = block[3:]
                self.source = code.rstrip('`').replace('```', '')


class GithubClient:
    def __init__(self, bot: Okiyu) -> None:
        self.bot = bot
        self.lock = asyncio.Lock()

    async def github_request(self, method, url, *, params=None, data=None, headers=None) -> dict | str:
        hdrs = {
            'Accept': 'application/vnd.github.inertia-preview+json',
            'User-Agent': 'Okiyu',
            'Authorization': f'token {os.getenv("GITHUB_TOKEN")}'
        }

        req_url = yarl.URL('https://api.github.com') / url

        if headers is not None and isinstance(headers, dict):
            hdrs.update(headers)

        await self.lock.acquire()
        try:
            async with self.bot.session.request(method, req_url, params=params, json=data, headers=hdrs) as r:
                remaining = r.headers.get('X-Ratelimit-Remaining')
                js = await r.json()
                if r.status == 429 or remaining == '0':
                    # wait before we release the lock
                    delta = disnake.utils._parse_ratelimit_header(r)
                    await asyncio.sleep(delta)
                    self.lock.release()
                    return await self.github_request(method, url, params=params, data=data, headers=headers)
                elif 300 > r.status >= 200:
                    return js
                else:
                    raise GithubError(js['message'])
        finally:
            if self.lock.locked():
                self.lock.release()

    async def create_gist(self, content, *, description=None, filename=None, public=True) -> str:
        headers = {
            'Accept': 'application/vnd.github.v3+json',
        }

        filename = filename or 'output.txt'
        data = {
            'public': public,
            'files': {
                filename: {
                    'content': content
                }
            }
        }

        if description:
            data['description'] = description

        js = await self.github_request('POST', 'gists', data=data, headers=headers)
        return js['html_url']

    async def get_user_info(self, url: str) -> disnake.Embed:
        data = await self.github_request('GET', url)
        if isinstance(data, str):
            em = disnake.Embed(
                title='Error!',
                description=data,
                color=utils.red
            )
            return em

        if data['name']:
            name = f'{data["name"]} ({data["login"]})'
        else:
            name = data['login']

        created_at = dateparser.parse(data['created_at'])

        em = disnake.Embed(
            title=name,
            description=data['bio'],
            color=utils.blurple,
            url=data['html_url'],
            timestamp=created_at,
        )

        em.set_footer(text='Joined')

        em.set_thumbnail(url=data['avatar_url'])

        em.add_field(
            name='Public Repos',
            value=data['public_repos'] or 'No public repos',
            inline=True,
        )

        if data['public_gists']:
            em.add_field(name='Public Gists', value=data['public_gists'], inline=True)

        value = [
            'Followers: ' + str(data['followers'])
            if data['followers']
            else 'Followers: no followers'
        ]
        value.append(
            'Following: ' + str(data['following'])
            if data['following']
            else 'Following: not following anyone'
        )

        em.add_field(name='Followers/Following', value='\n'.join(value), inline=True)

        if data['location']:
            em.add_field(name='Location', value=data['location'], inline=True)
        if data['company']:
            em.add_field(name='Company', value=data['company'], inline=True)
        if data['blog']:
            blog = data['blog']
            if blog.startswith('https://') or blog.startswith('http://'):
                pass
            else:
                blog = 'https://' + blog
            em.add_field(name='Website', value=blog, inline=True)

        return em

    async def get_repo_info(self, url: str) -> disnake.Embed:
        data = await self.github_request('GET', url)
        if isinstance(data, str):
            em = disnake.Embed(
                title='Error!',
                description=data,
                color=utils.red
            )
            return em

        created_at = dateparser.parse(data['created_at'])
        em = disnake.Embed(
            title=data['full_name'],
            color=utils.blurple,
            url=data['html_url'],
            timestamp=created_at,
        )

        # 2008-01-14T04:33:35Z

        em.set_footer(text='Created')

        owner = data['owner']

        em.set_author(
            name=owner['login'],
            url=owner['html_url'],
            icon_url=owner['avatar_url'],
        )
        em.set_thumbnail(url=owner['avatar_url'])

        description = data['description']
        if data['fork']:
            parent = data['parent']
            description = (
                f'Forked from [{parent["full_name"]}]({parent["html_url"]})\n\n' +
                description
            )

        if data['homepage']:
            description += '\n' + data['homepage']

        em.description = description

        em.add_field(name='Language', value=data['language'] or 'No language')
        em.add_field(
            name='Stars', value=data['stargazers_count'] or 'No Stars', inline=True
        )
        em.add_field(
            name='Watchers', value=data['watchers_count'] or 'No watchers', inline=True
        )
        em.add_field(name='Forks', value=data['forks_count'] or 'No forks', inline=True)

        return em
